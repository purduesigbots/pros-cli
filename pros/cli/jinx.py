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
    click.echo('building packet')
    packet = dict()
    # packet['type'] = int(msg.hex()[0:2], 16)
    timestamp = int(convert(msg.hex()[2:10]), 16)
    i = 10
    while i < len(msg.hex()):
        click.echo(f'{i} / {len(msg.hex())}: looping {msg.hex()}')
        msg_id = int(convert(msg.hex()[i + 4:i + 8]), 16)
        vsize = int(msg.hex()[i:i + 2], 16)
        if msg_id in schemas.keys():
            packet[schemas[msg_id][b'n']] = dict()
            i += 2
            click.echo('+2')
            packet[schemas[msg_id][b'n']]['timestamp'] = timestamp + int(msg.hex()[i:i + 2], 16)
            i += 6
            click.echo('+6')
            packet[schemas[msg_id][b'n']]['value'] = dict()
            x = bytearray.fromhex(msg.hex()[i:i + vsize * 2])
            y = struct.unpack(schemas[msg_id][b's'], x)
            if 'values' not in packet[schemas[msg_id][b'n']].keys():
                packet[schemas[msg_id][b'n']]['values'] = list()
            # roll list over
            packet[schemas[msg_id][b'n']]['values'] = packet[schemas[msg_id][b'n']]['values'][:DATA_HISTORY_MAX_COUNT]
            if len(y) > 1:
                v = dict()
                for j in range(len(y)):
                    k = schemas[msg_id][b'e'][j]
                    k = str(k, 'ascii') if isinstance(k, bytes) else k
                    v[k] = str(y[j], 'ascii') if isinstance(y[j], bytes) else y[j]
            else:
                v = str(y[j], 'ascii') if isinstance(y[j], bytes) else y[j]
            packet[schemas[msg_id][b'n']]['values'].append(v)
            i += vsize * 2
            click.echo(f'+{vsize * 2}')
        else:
            # 8 + vsize*2 = 2 + 2 + 4 + 2*size = len(size) + len(offset) + 2 * size [in bits]
            unknowns.append(msg[i:i + 8 + vsize * 2])
            i += 8 + vsize * 2
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

