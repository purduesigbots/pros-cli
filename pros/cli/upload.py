from pros.serial.ports import SerialPort
from pros.serial.vex import V5Device
from .common import *

import serial.serialutil


@click.group()
def upload_cli():
    pass


@upload_cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('port', type=str)
@click.argument('name', type=str, default=None, required=False)
@click.option('--slot', default=1, type=int)
@default_options
def upload(file: str, port: str, name: str=None, slot: int=1):
    try:
        ser = SerialPort(port)
        v5 = V5Device(ser)
        if name is None:
            name = os.path.splitext(os.path.basename(file))[0]
        with click.open_file(file, mode='rb') as pf:
            v5.write_program(pf, name, slot=slot-1, run_after=True)
    except Exception as e:
        logger(__name__).debug(e, exc_info=True)
        click.echo(e, err=True)
        exit(1)
