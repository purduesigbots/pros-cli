import logging
import os
import signal

import click

import pros
import pros.serial.ports as ports
from pros.common.utils import logger
from pros.serial.terminal import Terminal


@click.group()
def terminal_cli():
    pass


@terminal_cli.command()
@click.argument('port', default='default')
@click.option('--backend', type=click.Choice(['share', 'solo']), default='share',
              help='Backend port of the terminal. See above for details')
@click.option('--raw', is_flag=True, default=False,
              help='Don\'t process the data. If on the "share" backend, '
                   'then this option has no effect if connecting to an existing bridge')
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
        click.echo('Default port picking isn\'t implemented yet!')
        return

    if backend == 'share':
        ser = ports.SerialSharePort(port)
    else:
        ser = ports.SerialPort(port)
    term = Terminal(ser)
    signal.signal(signal.SIGINT, term.stop)
    term.start()
    term.join()
    logger(__name__).info('CLI Main Thread Dying')
    os._exit(0)  # _exit(0) so that SerialShareBridge may continue running
