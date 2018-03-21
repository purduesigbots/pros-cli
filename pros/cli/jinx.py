import asyncio
import click
import msgpack
import json
import struct
from typing import Any, Dict
import websockets

import pros.serial.ports as ports
import pros.serial.vex.v5_device as v5_device
from .common import PROSGroup, default_options


DATA_HISTORY_MAX_COUNT = 500
schemas = dict()
unknowns = list()
ser: ports.DirectPort = None


def convert(b: str) -> str:
    return ''.join(reversed([b[i:i+2] for i in range(0, len(b), 2)]))


@click.group(cls=PROSGroup)
def jinx_cli():
    pass


def create_packet(msg: bytes) -> Dict[str, Any]:
    """
    create a packet for the JINX frontend
    :param msg: message read from serial line
    :return: packet of the form
            {
                'field_name': {
                    'timestamp': List[int],
                    'values': List[Union[int, chr, str, Dict[str, Any]]]
                },
            }
            timestamps and values are kept as rolling lists in case value history needs to be accessed at any time
    """
    BASE_HEX = 16
    
    #Value message protocol constants
    #All lengths in bytes
    T_STAMP_IDX = 2                         #Start index in bytes within the given msg
    T_STAMP_LEN = 8                         #Length of timestamp
    VAL_ID_LEN = 2                          #Length of Value ID
    VAL_SIZE_LEN = 1                        #Length of field "Value Size". This field indicates how much data should be read
    OFFSET_LEN = 2                          #Length of timestamp offset. Only one timestamp is sent in a bundle
    
    #Schema message protocol constants
    #The schema is a dictionary using the byte representation of characters as keys
    #See PDN 3.003 Schema Message Protocol for most up-to-date information
    SCHEMA_NAME = b'n'                      #Human readable name of field
    SCHEMA_SFS = b's'                       #Struct format string
    SCHEMA_ELEMENTS = b'e'                  #List of human-readable element names corresponding to what is unpacked in the SFS
    SCHEMA_MUTABLE = b'm'                   #True if the value can be edited on the Brain
    
    #Packet constants
    #Strings representing parsable javascript identifiers
    PACKET_TSTAMP = "timestamp"             #Time data was generated on brain
    PACKET_VALS = "values"                  #dictionary of all elements, or else single element
    
    click.echo('building packet')
    packet = dict()
    # packet['type'] = int(msg.hex()[0:2], 16)
    timestamp = int(convert(msg.hex()[T_STAMP_IDX:T_STAMP_IDX + T_STAMP_LEN]), BASE_HEX)
    byte_idx = T_STAMP_IDX + T_STAMP_LEN
    
    while byte_idx < len(msg.hex()):
        click.echo(f'{byte_idx} / {len(msg.hex())}: looping {msg.hex()}')
        msg_id = int(convert(msg.hex()[byte_idx + 4:byte_idx + 8]), BASE_HEX)
        vsize = int(msg.hex()[byte_idx:byte_idx + 2], BASE_HEX)
        
        if msg_id in schemas.keys():
            schema = schemas[msg_id]
            name = schema[SCHEMA_NAME]
            elements = schema[SCHEMA_ELEMENTS]
            struct_fs = schema[SCHEMA_SFS]   #Struct format string
            mutable = schema[SCHEMA_MUTABLE]
            
            packet[name] = dict()           #Will contain field timestamp and a dictionary of values
            byte_idx += VAL_ID_LEN
            click.echo('+2')
            
            packet[name][PACKET_TSTAMP] = timestamp + int(msg.hex()[byte_idx:byte_idx + OFFSET_LEN], BASE_HEX)
            byte_idx += 6                   #TODO: Figure out what is being skipped here
            click.echo('+6')

            packet[name][PACKET_VALS] = dict()
            x = bytearray.fromhex(msg.hex()[byte_idx:byte_idx + vsize * 2]) #TODO: Figure out why size is multiplied by 2
            vals = struct.unpack(struct_fs, x)
            
            if PACKET_VALS not in packet[name].keys():
                packet[name][PACKET_VALS] = list()
            
            # roll list over        #TODO: What is a rollover? This list is getting the end chopped off
            packet[name][PACKET_VALS] = packet[name][PACKET_VALS][:DATA_HISTORY_MAX_COUNT]
            if len(vals) > 1:
                packet_val = dict()
                for val_idx in range(len(vals)):
                    element = elements[j]
                    element = str(element, 'ascii') if isinstance(element, bytes) else element
                    packet_val[element] = str(vals[val_idx], 'ascii') if isinstance(vals[val_idx], bytes) else vals[val_idx]
            else:
                packet_val = str(vals[val_idx], 'ascii') if isinstance(vals[val_idx], bytes) else vals[val_idx]
            
            packet[name][PACKET_VALS].append(packet_val)
            byte_idx += vsize * 2
            click.echo(f'+{vsize * 2}')
        else:
            # 8 + vsize*2 = 2 + 2 + 4 + 2*size = len(size) + len(offset) + 2 * size [in bits]
            unknowns.append(msg[byte_idx:byte_idx + 8 + vsize * 2])
            byte_idx += 8 + vsize * 2
            click.echo(f'+14+{vsize}*2 ({8+vsize*2})')

    click.echo(packet)
    return packet


async def poll_and_send_data(websocket, path):
    click.echo('in poll')
    while True:
        stream, msg = ser.read()
        # click.echo(str(stream, 'ascii'))
        # click.echo(msg.hex())
        if stream == b'jinx':
            if msg[0] == b'S'[0]:
                # click.echo(msg.hex())
                schema = msgpack.unpackb(bytearray.fromhex(msg.hex()[2:]))
                # click.echo(msgpack.unpackb(bytearray.fromhex(msg.hex()[2:])))
                schemas.update(schema)
                for msg in unknowns:
                    packet = create_packet(msg)
                    click.echo(json.dumps(packet))
                    await websocket.send(json.dumps(packet))
            elif msg[0] == b'D'[0]:
                packet = create_packet(msg)
                # click.echo(packet)
                click.echo(json.dumps(packet))
                await websocket.send(json.dumps(packet))


@jinx_cli.command(short_help='Run JINX, the graphical debugger for PROS')
@default_options
def jinx():
    """
    JINX is PROS's graphical debugger. This command runs the JINX webserver

    Visit https://pros.cs.purdue.edu/v5/cli/jinx to learn more
    """
    global ser
    _ports = [p.device for p in v5_device.find_v5_ports('user')]
    if len(_ports) > 1:
        port = click.prompt('Multiple V5 ports were found. Please pick one.',
                            type=click.Choice(_ports), default=_ports[0], show_default=True)
    else:
        port = _ports[0]
    ser = ports.DirectPort(port)
    ser.config('cobs', True)
    click.echo('starting server')
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(poll_and_send_data, 'localhost', 9001)
    loop.run_until_complete(start_server)
    loop.run_forever()
    click.echo('after server')

