from .click_classes import *
from .common import *

from pros.common import *

from pros.serial.ports import DirectPort
from pros.serial.vex import find_v5_ports, V5Device


@click.group()
def v5_utils_cli():
    pass


@v5_utils_cli.group(cls=PROSGroup)
@default_options
def v5():
    pass


@v5.command()
@click.argument('port', required=False, default=None)
@default_options
def status(port: str):
    """
    Print system information for the V5
    """
    port = resolve_v5_port(port, 'system')
    if not port:
        return -1

    ser = DirectPort(port)
    device = V5Device(ser)
    status = device.get_system_status()
    if ismachineoutput():
        print(status)
    else:
        print('Connected to V5 on {}'.format(port))
        print('System version:', '{}.{}.{}b{}'.format(*status['system_version']))
        print('CPU0 F/W version:', '{}.{}.{}b{}'.format(*status['cpu0_version']))
        print('CPU1 SDK version:', '{}.{}.{}b{}'.format(*status['cpu1_version']))
        print('System ID: 0x{:x}'.format(status['system_id']))


@v5.command('ls-files')
@click.option('--vid', type=int, default=1, cls=PROSOption, hidden=True)
@click.option('--options', type=int, default=0, cls=PROSOption, hidden=True)
@click.argument('port', required=False, default=None)
@default_options
def ls_files(port: str, vid: int, options: int):
    """
    List files on the flash filesystem
    """
    port = resolve_v5_port(port, 'system')
    if not port:
        return -1

    ser = DirectPort(port)
    device = V5Device(ser)
    c = device.get_dir_count(vid=vid, options=options)
    for i in range(0, c):
        print(device.get_file_metadata_by_idx(i))


@v5.command(hidden=True)
@click.argument('file_name')
@click.argument('port', required=False, default=None)
@click.argument('outfile', required=False, default=click.get_binary_stream('stdout'), type=click.File('wb'))
@click.option('--vid', type=int, default=1, cls=PROSOption, hidden=True)
@click.option('--source', type=click.Choice(['ddr', 'flash']), default='flash', cls=PROSOption, hidden=True)
@default_options
def read_file(file_name: str, port: str, vid: int, source: str):
    """
    Read file on the flash filesystem to stdout
    """
    port = resolve_v5_port(port, 'system')
    if not port:
        return -1

    ser = DirectPort(port)
    device = V5Device(ser)
    device.read_file(file=click.get_binary_stream('stdout'), remote_file=file_name,
                     vid=vid, target=source)


@v5.command(hidden=True)
@click.argument('file', type=click.File('rb'))
@click.argument('port', required=False, default=None)
@click.option('--addr', type=int, default=0x03800000, required=False)
@click.option('--remote-file', required=False, default=None)
@click.option('--run-after/--no-run-after', 'run_after', default=False)
@click.option('--vid', type=int, default=1, cls=PROSOption, hidden=True)
@click.option('--target', type=click.Choice(['ddr', 'flash']), default='flash')
@default_options
def write_file(file, port: str, remote_file: str, **kwargs):
    """
    Write a file to the V5.
    """
    port = resolve_v5_port(port, 'system')
    if not port:
        return -1

    ser = DirectPort(port)
    device = V5Device(ser)
    device.write_file(file=file, remote_file=remote_file or os.path.basename(file.name), **kwargs)


@v5.command('rm-file')
@click.argument('file_name')
@click.argument('port', required=False, default=None)
@click.option('--vid', type=int, default=1, cls=PROSOption, hidden=True)
@click.option('--erase-all/--erase-only', 'erase_all', default=False, show_default=True,
              help='Erase all files matching base name.')
@default_options
def rm_file(file_name: str, port: str, vid: int, erase_all: bool):
    """
    Remove a file from the flash filesystem
    """
    port = resolve_v5_port(port, 'system')
    if not port:
        return -1

    ser = DirectPort(port)
    device = V5Device(ser)
    device.erase_file(file_name, vid=vid, erase_all=erase_all)


