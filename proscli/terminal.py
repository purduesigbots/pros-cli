import click
import proscli.serial_terminal
import prosflasher.ports
import signal
import sys
import time


@click.group()
def terminal_cli():
    pass


@terminal_cli.command(short_help='Open terminal with the microcontroller')
@click.argument('port', default='default')
def terminal(port):
    click.echo(click.style('NOTE: This is an early prototype of the terminal.'
                           ' Nothing is guaranteed to work.', bold=True))
    if port == 'default':
        if len(prosflasher.ports.list_com_ports()) == 1:
            port = prosflasher.ports.list_com_ports()[0].device
        elif len(prosflasher.ports.list_com_ports()) > 1:
            click.echo('Multiple ports were found:')
            click.echo(prosflasher.ports.create_port_list())
            port = click.prompt('Select a port to open',
                                type=click.Choice([p.device for p in prosflasher.ports.list_com_ports()]))
        else:
            click.echo('No ports were found.')
            click.get_current_context().abort()
            sys.exit()
    ser = prosflasher.ports.create_serial(port)
    term = proscli.serial_terminal.Terminal(ser)
    signal.signal(signal.SIGINT, term.stop)
    term.start()
    while term.alive:
        time.sleep(0.005)
    term.join()
    ser.close()
    print('Exited successfully')
    sys.exit(0)