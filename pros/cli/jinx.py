import click
import msgpack

import pros.serial.ports as ports
import pros.serial.vex.v5_device as v5_device
from .common import PROSGroup, default_options

def convert(bytestring):
	return b''.join(reversed([bytestring[i:i+2] for i in range(0,len(bytestring),2)]))

@click.group(cls=PROSGroup)
def jinx_cli():
    pass


@jinx_cli.command(short_help='Run JINX, the graphical debugger for PROS')
@default_options
def jinx():
    """
    JINX is PROS's graphical debugger. This command runs the JINX webserver

    Visit https://pros.cs.purdue.edu/v5/cli/jinx to learn more
    """
    _ports = [p.device for p in v5_device.find_v5_ports('user')]
    if len(_ports) > 1:
        port = click.prompt('Multiple V5 ports were found. Please pick one.',
                            type=click.Choice(_ports), default=_ports[0], show_default=True)
    else:
        port = _ports[0]
    ser = ports.DirectPort(port)
    ser.config('cobs', True)
    while True:
        stream, msg = ser.read()
        if stream == b'jinx':
            if msg[0] == b'S'[0]:
                click.echo(msg.hex())
                click.echo(msgpack.unpackb(msg[1:]))
            elif msg[0] == b'D'[0]:
				packet = {}
				packet['type'] = msg[0]
				packet['timestamp'] = convert(msg[1:5])
				packet['data'] = []
				i = 5
				while i < len(msg):
					packet['data'].append({})
					id = convert(msg[i+3:i+7])
					packet['data'][-1][id] = []
					packet['data'][-1][id].append({})
					packet['data'][-1][id][-1]['size'] = msg[i:i+2]
					i += 2
					packet['data'][-1][id][-1]['offset'] = msg[i:i+2]
					i += 6
					packet['data'][-1][id][-1]['value'] = msg[i:i + int(packet['data'][-1][id][-1]['size']) * 2]
					i += int(packet['data'][-1][id][-1]['size']) * 2
				click.echo(packet)
