import os
import signal
import time

import click

import pros.conductor as c
import pros.serial.ports as ports
import pros.serial.vex.cortex_device as cortex_device
import pros.serial.vex.v5_device as v5_device
from pros.common.utils import logger
from pros.serial.terminal import Terminal
from .click_classes import PROSGroup
from .common import default_options


@click.group(cls=PROSGroup)
def terminal_cli():
    pass


@terminal_cli.command()
@default_options
@click.argument('port', default='default')
@click.option('--backend', type=click.Choice(['share', 'solo']), default='solo',
              help='Backend port of the terminal. See above for details')
@click.option('--raw', is_flag=True, default=False,
              help='Don\'t process the data.')
@click.option('--hex', is_flag=True, default=False, help="Display data as hexadecimal values. Unaffected by --raw")
@click.option('--ports', nargs=2, type=int, default=(None, None),
              help='Specify 2 ports for the "share" backend. The default option deterministically selects ports '
                   'based on the serial port name')
def terminal(port: str, backend: str, **kwargs):
    """
    Open a terminal to a serial port

    There are two possible backends for the terminal: "share" or "solo". In "share" mode, a server/bridge is created
    so that multiple PROS processes (such as another terminal or flash command) may communicate with the device. In the
    simpler solo mode, only one PROS process may communicate with the device. The default mode is "share", but "solo"
    may be preferred when "share" doesn't perform adequately.
    """
    if port == 'default':
        project_path = c.Project.find_project(os.getcwd())
        if project_path is None:
            logger(__name__).error('You must be in a PROS project directory to enable default port selecting')
            return -1
        project = c.Project(project_path)
        port = project.target

    if port == 'v5':
        _ports = [p.device for p in v5_device.find_v5_ports('user')]
        if len(_ports) > 1:
            port = click.prompt('Multiple V5 ports were found. Please pick one.',
                                type=click.Choice(_ports), default=_ports[0], show_default=True)
        else:
            port = _ports[0]
    elif port == 'cortex':
        _ports = [p.device for p in cortex_device.find_cortex_ports()]
        if len(_ports) > 1:
            port = click.prompt('Multiple Cortex ports were found. Please pick one.',
                                type=click.Choice(_ports), default=_ports[0], show_default=True)
        else:
            port = _ports[0]

    if backend == 'share':
        ser = ports.SerialSharePort(port)
    else:
        ser = ports.DirectPort(port)
        if not kwargs['raw']:
            ser.config('cobs', True)
    term = Terminal(ser)

    signal.signal(signal.SIGINT, term.stop)
    term.start()
    while not term.alive.is_set():
        time.sleep(0.005)
    term.join()
    logger(__name__).info('CLI Main Thread Dying')
