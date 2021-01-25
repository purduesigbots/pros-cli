import os
import signal
import time

import click

import pros.conductor as c
import pros.serial.devices as devices
from pros.serial.ports import DirectPort
from pros.common.utils import logger
from .common import default_options, resolve_v5_port, resolve_cortex_port, pros_root
from pros.serial.ports.v5_wireless_port import V5WirelessPort


@pros_root
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
@click.option('--banner/--no-banner', 'request_banner', default=True)
def terminal(port: str, backend: str, **kwargs):
    """
    Open a terminal to a serial port

    There are two possible backends for the terminal: "share" or "solo". In "share" mode, a server/bridge is created
    so that multiple PROS processes (such as another terminal or flash command) may communicate with the device. In the
    simpler solo mode, only one PROS process may communicate with the device. The default mode is "share", but "solo"
    may be preferred when "share" doesn't perform adequately.

    Note: share backend is not yet implemented.
    """
    from pros.serial.devices.vex.v5_user_device import V5UserDevice
    from pros.serial.terminal import Terminal
    is_v5_user_joystick = False
    if port == 'default':
        project_path = c.Project.find_project(os.getcwd())
        if project_path is None:
            v5_port, is_v5_user_joystick = resolve_v5_port(None, 'user', quiet=True)
            cortex_port = resolve_cortex_port(None, quiet=True)
            if ((v5_port is None) ^ (cortex_port is None)) or (v5_port is not None and v5_port == cortex_port):
                port = v5_port or cortex_port
            else:
                raise click.UsageError('You must be in a PROS project directory to enable default port selecting')
        else:
            project = c.Project(project_path)
            port = project.target

    if port == 'v5':
        port = None
        port, is_v5_user_joystick = resolve_v5_port(port, 'user')
    elif port == 'cortex':
        port = None
        port = resolve_cortex_port(port)
        kwargs['raw'] = True
    if not port:
        return -1

    if backend == 'share':
        raise NotImplementedError('Share backend is not yet implemented')
        # ser = SerialSharePort(port)
    elif is_v5_user_joystick:
        logger(__name__).debug("it's a v5 joystick")
        ser = V5WirelessPort(port)
    else:
        logger(__name__).debug("not a v5 joystick")
        ser = DirectPort(port)
    if kwargs.get('raw', False):
        device = devices.RawStreamDevice(ser)
    else:
        device = devices.vex.V5UserDevice(ser)
    term = Terminal(device, request_banner=kwargs.pop('request_banner', True))

    signal.signal(signal.SIGINT, term.stop)
    term.start()
    while not term.alive.is_set():
        time.sleep(0.005)
    term.join()
    logger(__name__).info('CLI Main Thread Dying')
