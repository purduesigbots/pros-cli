import click
import os
import sys
import prosflasher.ports
import prosflasher.upload


@click.group()
def flasher_cli():
    pass


@flasher_cli.command(short_help='Upload binaries to the microcontroller.')
@click.option('-sfs/-dfs', '--save-file-system/--delete-file-system', is_flag=True, default=False,
              help='Specify whether or not to save the file system when writing to the Cortex. Saving the '
                   'file system takes more time.')
@click.option('-y', is_flag=True, default=False,
              help='Automatically say yes to all confirmations.')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Display more verbose output')
@click.option('-f', '-b', '--file', '--binary', default='default', metavar='FILE',
              help='Specify file if file detection fails')
@click.argument('port', default='auto')
# @click.option('-m', '--strategy', default='cortex', metavar='STRATEGY',
#               help='Specify the microcontroller upload strategy. Not currently used.')
def flash(save_file_system, y, verbose, port, binary):
    """Upload binaries to the microcontroller. A serial port and binary file need to be specified.

    By default, the port is automatically selected (if you want to be pendantic, 'auto').
    Otherwise, a system COM port descriptor needs to be used. In Windows/NT, this takes the form of COM1.
    In *nx systems, this takes the form of /dev/tty1 or /dev/acm1 or similar.
    \b
    Specifying 'all' as the COM port will automatically upload to all available microcontrollers.

    By default, the CLI will look around for a proper binary to upload to the microcontroller. If one was not found, or
    if you want to change the default binary, you can specify it.
    """
    if port == 'auto':
        ports = prosflasher.ports.list_com_ports()
        if len(ports) == 0:
            click.echo('No microcontrollers were found. Please plug in a cortex or manually specify a serial port.\n',
                       err=True)
            exit(1)
        port = prosflasher.ports.list_com_ports()[0].device
        if port is not None and y is False:
            click.confirm('Download to ' + port, default=True, abort=True, prompt_suffix='?')
    if port == 'all':
        port = [p.device for p in prosflasher.ports.list_com_ports()]
        if len(port) == 0:
            click.echo('No microcontrollers were found. Please plug in a cortex or manually specify a serial port.\n',
                       err=True)
            exit(1)
        if y is False:
            click.confirm('Download to ' + ', '.join(port), default=True, abort=True, prompt_suffix='?')
    else:
        port = [port]

    if binary == 'default':
        binary = find_file('output.bin', '.', 'bin')
        if binary is None:
            binary = find_file('output.bin', '..', 'bin')
            if binary is None:
                click.echo('Unable to find a binary file. Please specify it.', err=True)
                exit(1)

    click.echo('Flashing ' + binary + ' to ' + ', '.join(port))
    for p in port:
        prosflasher.upload.upload(p, binary, verbose)


def find_file(file_name, directory, recurse_dir=None):
    for root, dirs, files in os.walk(directory):
        if file_name in files:
            return os.path.join(directory, file_name)
        if recurse_dir in dirs:
            return find_file(file_name, os.path.join(directory, recurse_dir), recurse_dir)
    return None


@flasher_cli.command('poll', short_help='Polls a microcontroller for its system info')
@click.option('-y', is_flag=True, default=False,
              help='Automatically say yes to all confirmations.')
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.argument('port', default='auto')
def get_sys_info(y, verbose, port):
    prosflasher.upload.set_verbosity(verbose)
    if port == 'auto':
        ports = prosflasher.ports.list_com_ports()
        if len(ports) == 0:
            click.echo('No microcontrollers were found. Please plug in a cortex or manually specify a serial port.\n',
                       err=True)
            exit(1)
        port = prosflasher.ports.list_com_ports()[0].device
        if port is not None and y is False:
            click.confirm('Poll ' + port, default=True, abort=True, prompt_suffix='?')
    if port == 'all':
        port = [p.device for p in prosflasher.ports.list_com_ports()]
        if len(port) == 0:
            click.echo('No microcontrollers were found. Please plug in a cortex or manually specify a serial port.\n',
                       err=True)
            exit(1)
        if y is False:
            click.confirm('Poll ' + ', '.join(port), default=True, abort=True, prompt_suffix='?')
    else:
        port = [port]

    for p in port:
        sys_info = prosflasher.upload.ask_sys_info(prosflasher.ports.create_serial(p))
        click.echo(repr(sys_info))

    pass


@flasher_cli.command(short_help='List connected microcontrollers')
@click.option('-v', '--verbose', is_flag=True)
def lsusb(verbose):
    click.echo(prosflasher.ports.create_port_list(verbose))


@flasher_cli.command(name='dump-cortex', short_help='Dumps user flash contents to a specified file')
@click.option('-v', '--verbose', is_flag=True)
@click.argument('file', default=sys.stdout, type=click.File())
def dump_cortex(file, verbose):
    pass
