import click
import pros.serial.terminal as term
import pros.serial.ports as ports


@click.group()
def terminal_cli():
    pass


@terminal_cli.command()
@click.argument('port', default='default')
def terminal(port):
    if port == 'default':
        click.echo('Default port picking isn\'t implemented yet!')
        return

    ser = ports.create_serial(port)
    term.display_terminal(ser)
    ser.close()
