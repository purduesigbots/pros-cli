import click
import os
import os.path
import ntpath
import sys
import prosflasher.ports
import prosflasher.upload
import prosconfig
from proscli.utils import default_cfg, AliasGroup


@click.group(cls=AliasGroup)
def flasher_cli():
    pass


@flasher_cli.command(short_help='Upload binaries to the microcontroller.', aliases=['upload'])
@click.option('-sfs/-dfs', '--save-file-system/--delete-file-system', is_flag=True, default=False,
              help='Specify whether or not to save the file system when writing to the Cortex. Saving the '
                   'file system takes more time.')
@click.option('-y', is_flag=True, default=False,
              help='Automatically say yes to all confirmations.')
@click.option('-f', '-b', '--file', '--binary', default='default', metavar='FILE',
              help='Specifies a binary file, project directory, or project config file.')
@click.option('-p', '--port', default='auto', metavar='PORT', help='Specifies the serial port.')
@click.option('--no-poll', is_flag=True, default=False)
@default_cfg
# @click.option('-m', '--strategy', default='cortex', metavar='STRATEGY',
#               help='Specify the microcontroller upload strategy. Not currently used.')
def flash(ctx, save_file_system, y, port, binary, no_poll):
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
            click.get_current_context().abort()
            sys.exit(1)
        port = ports[0].device
        if len(ports) > 1 and port is not None and y is False:
            click.confirm('Download to ' + port, default=True, abort=True, prompt_suffix='?')
    if port == 'all':
        port = [p.device for p in prosflasher.ports.list_com_ports()]
        if len(port) == 0:
            click.echo('No microcontrollers were found. Please plug in a cortex or manually specify a serial port.\n',
                       err=True)
            click.get_current_context().abort()
            sys.exit(1)
        if y is False:
            click.confirm('Download to ' + ', '.join(port), default=True, abort=True, prompt_suffix='?')
    else:
        port = [port]

    if binary == 'default':
        binary = os.getcwd()
        if ctx.verbosity > 3:
            click.echo('Default binary selected, new directory is {}'.format(binary))

    binary = find_binary(binary)

    if binary is None:
        click.echo('No binary was found! Ensure you are in a built PROS project (run make) '
                   'or specify the file with the -f flag',
                   err=True)
        click.get_current_context().exit()

    if ctx.verbosity > 3:
        click.echo('Final binary is {}'.format(binary))

    click.echo('Flashing ' + binary + ' to ' + ', '.join(port))
    for p in port:
        prosflasher.upload.upload(p, binary, no_poll, ctx)


def find_binary(path):
    """
    Helper function for finding the binary associated with a project

    The algorithm is as follows:
        - if it is a file, then check if the name of the file is 'pros.config':
            - if it is 'pros.config', then find the binary based off the pros.config value (or default 'bin/output.bin')
            - otherwise, can only assume it is the binary file to upload
        - if it is a directory, start recursively searching up until 'pros.config' is found. max 10 times
            - if the pros.config file was found, find binary based off of the pros.config value
            - if no pros.config file was found, start recursively searching up (from starting path) until a directory
                named bin is found
                - if 'bin' was found, return 'bin/output.bin'
    :param path: starting path to start the search
    :param ctx:
    :return:
    """
    # logger = logging.getLogger(ctx.log_key)
    # logger.debug('Finding binary for {}'.format(path))
    if os.path.isfile(path):
        if ntpath.basename(path) == 'pros.config':
            pros_cfg = prosconfig.ProjectConfig(path)
            return os.path.join(path, pros_cfg.output)
        return path
    elif os.path.isdir(path):
        try:
            cfg = prosconfig.ProjectConfig(path, raise_on_error=True)
            if cfg is not None and os.path.isfile(os.path.join(cfg.directory, cfg.output)):
                return os.path.join(cfg.directory, cfg.output)
        except prosconfig.ConfigNotFoundException:
            search_dir = path
            for n in range(10):
                dirs = [d for d in os.listdir(search_dir)
                        if os.path.isdir(os.path.join(path, search_dir, d)) and d == 'bin']
                if len(dirs) == 1:  # found a bin directory
                    if os.path.isfile(os.path.join(path, search_dir, 'bin', 'output.bin')):
                        return os.path.join(path, search_dir, 'bin', 'output.bin')
                search_dir = ntpath.split(search_dir)[:-1][0]  # move to parent dir
    return None


@flasher_cli.command('poll', short_help='Polls a microcontroller for its system info')
@click.option('-y', '--yes', is_flag=True, default=False,
              help='Automatically say yes to all confirmations.')
@click.argument('port', default='all')
@default_cfg
def get_sys_info(cfg, yes, port):
    if port == 'auto':
        ports = prosflasher.ports.list_com_ports()
        if len(ports) == 0:
            click.echo('No microcontrollers were found. Please plug in a cortex or manually specify a serial port.\n',
                       err=True)
            sys.exit(1)
        port = prosflasher.ports.list_com_ports()[0].device
        if port is not None and yes is False:
            click.confirm('Poll ' + port, default=True, abort=True, prompt_suffix='?')
    if port == 'all':
        port = [p.device for p in prosflasher.ports.list_com_ports()]
        if len(port) == 0:
            click.echo('No microcontrollers were found. Please plug in a cortex or manually specify a serial port.\n',
                       err=True)
            sys.exit(1)
    else:
        port = [port]

    for p in port:
        sys_info = prosflasher.upload.ask_sys_info(prosflasher.ports.create_serial(p))
        click.echo(repr(sys_info))

    pass


@flasher_cli.command(short_help='List connected microcontrollers')
@default_cfg
def lsusb(cfg):
    if len(prosflasher.ports.list_com_ports()) == 0 or prosflasher.ports.list_com_ports() is None:
        click.echo('No serial ports found.')
    else:
        click.echo('Available Ports:')
        click.echo(prosflasher.ports.create_port_list(cfg.verbosity > 0))


# @flasher_cli.command(name='dump-cortex', short_help='Dumps user flash contents to a specified file')
# @click.option('-v', '--verbose', is_flag=True)
# @click.argument('file', default=sys.stdout, type=click.File())
# def dump_cortex(file, verbose):
#     pass
