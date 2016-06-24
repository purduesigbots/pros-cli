import click
import serial
import serial.tools.miniterm
import prosflasher.ports
import threading


@click.group()
def terminal_cli():
    pass


@terminal_cli.command(short_help='Open terminal with the microcontroller')
@click.argument('port', default='default')
def terminal(port):
    if port == 'default':
        if len(prosflasher.ports.list_com_ports()) == 1:
            port = prosflasher.ports.list_com_ports()[0].device
        elif len(prosflasher.ports.list_com_ports()) > 1:
            click.echo('Multiple ports were found:')

            port = click.prompt('Multiple ports found. Please se')
        else:
            click.echo('No ports were found.')
            exit()

    ser = prosflasher.ports.create_serial(port)
    term = serial.tools.miniterm.Miniterm(ser, echo=click.echo)
    term.set_rx_encoding('UTF-8')
    term.set_tx_encoding('UTF-8')
    term.exit_character = '\x03'
    try:
        term.start()
        term.join()
    except KeyboardInterrupt:
        pass
    except serial.serialutil.SerialException:
        click.echo('Disconnected from microcontroller')
    term.close()
