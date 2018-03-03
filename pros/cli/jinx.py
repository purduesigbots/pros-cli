import click
import msgpack

import pros.serial.ports as ports
import pros.serial.vex.v5_device as v5_device
from .common import PROSGroup, default_options


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
            else:
                click.echo(msg.hex())
