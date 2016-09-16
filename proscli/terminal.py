import click
import proscli.serial_terminal
import prosflasher.ports
import sys


@click.group()
def terminal_cli():
    pass


@terminal_cli.command(short_help='Open terminal with the microcontroller')
@click.argument('port', default='default')
def terminal(port):
    click.echo(click.style('NOTE: This is an early prototype of the terminal. Nothing is guaranteed to work.',
                           blink=True, bold=True))
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
    term.start()
    while(term.alive):
        pass
    term.join()
    ser.close()
    # term = serial.tools.miniterm.Miniterm(ser, echo=click.echo)
    # term.set_rx_encoding('UTF-8')
    # term.set_tx_encoding('UTF-8')
    # term.exit_character = '\x03'
    # try:
    #     term.start()
    #     term.join()
    # except KeyboardInterrupt:
    #     pass
    # except serial.serialutil.SerialException:
    #     click.echo('Disconnected from microcontroller')
    # term.close()
