from .click_classes import *
from .common import *


@pros_root
def v5_utils_cli():
    pass


@v5_utils_cli.group(cls=PROSGroup, help='Utilities for managing the VEX V5')
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
    from pros.serial.devices.vex import V5Device
    from pros.serial.ports import DirectPort
    port = resolve_v5_port(port, 'system')
    if not port:
        return -1

    ser = DirectPort(port)
    device = V5Device(ser)
    if ismachineoutput():
        print(device.status)
    else:
        print('Connected to V5 on {}'.format(port))
        print('System version:', device.status['system_version'])
        print('CPU0 F/W version:', device.status['cpu0_version'])
        print('CPU1 SDK version:', device.status['cpu1_version'])
        print('System ID: 0x{:x}'.format(device.status['system_id']))


@v5.command('ls-files')
@click.option('--vid', type=int, default=1, cls=PROSOption, hidden=True)
@click.option('--options', type=int, default=0, cls=PROSOption, hidden=True)
@click.argument('port', required=False, default=None)
@default_options
def ls_files(port: str, vid: int, options: int):
    """
    List files on the flash filesystem
    """
    from pros.serial.devices.vex import V5Device
    from pros.serial.ports import DirectPort
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
    from pros.serial.devices.vex import V5Device
    from pros.serial.ports import DirectPort
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
    from pros.serial.ports import DirectPort
    from pros.serial.devices.vex import V5Device
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
    from pros.serial.devices.vex import V5Device
    from pros.serial.ports import DirectPort
    port = resolve_v5_port(port, 'system')
    if not port:
        return -1

    ser = DirectPort(port)
    device = V5Device(ser)
    device.erase_file(file_name, vid=vid, erase_all=erase_all)


@v5.command('rm-all')
@click.argument('port', required=False, default=None)
@click.option('--vid', type=int, default=1, hidden=True, cls=PROSOption)
@default_options
def rm_all(port: str, vid: int):
    """
    Remove all user programs from the V5
    """
    from pros.serial.devices.vex import V5Device
    from pros.serial.ports import DirectPort
    port = resolve_v5_port(port, 'system')
    if not port:
        return -1

    ser = DirectPort(port)
    device = V5Device(ser)
    c = device.get_dir_count(vid=vid)
    files = []
    for i in range(0, c):
        files.append(device.get_file_metadata_by_idx(i)['filename'])
    for file in files:
        device.erase_file(file, vid=vid)


@v5.command('rm-slot')
@click.argument('slot')
@click.argument('port', required=False, default=None)
@default_options
def rm_slot(slot: str, port: str):
    """
    Remove a program from the V5 by slot number or name.
    """
    from pros.serial.devices.vex import V5Device
    from pros.serial.ports import DirectPort
    import io
    port = resolve_v5_port(port, 'system')
    if not port:
        return -1

    ser = DirectPort(port)
    device = V5Device(ser)
    c = device.get_dir_count()
    files = []
    for i in range(0, c):
        metadata = device.get_file_metadata_by_idx(i)
        if metadata['type'] == 'ini':
            f = io.BytesIO()
            device.read_file(f, metadata['filename'])
            f.seek(0, 0)
            print(f.readlines())

    for file in files:
        device.erase_file(file)


@v5.command(short_help='Run a V5 Program')
@click.argument('file', required=False, default=None)
@click.argument('port', required=False, default=None)
@default_options
def run(file: str, port: str):
    """
    Run a V5 program

    If FILE is unspecified or is a directory, then attempts to find the correct filename based on the PROS project
    """
    from pros.serial.devices.vex import V5Device
    from pros.serial.ports import DirectPort
    import re
    if not file or os.path.isdir(file):
        import pros.conductor as c
        path = c.Project.find_project(file)
        if path:
            file = f'{c.Project(path).name}.bin'
    elif not re.match(r'[\w\.]{1,24}', file):
        logger(__name__).error('file must be a valid V5 filename')
        return 1
    port = resolve_v5_port(port, 'system')
    ser = DirectPort(port)
    device = V5Device(ser)
    device.execute_program_file(file, run=True)


@v5.command(short_help='Stop a V5 Program')
@click.argument('file', required=False, default=None)
@click.argument('port', required=False, default=None)
@default_options
def stop(file: str, port: str):
    """
    Stops a V5 program

    If FILE is unspecified or is a directory, then attempts to find the correct filename based on the PROS project
    """
    from pros.serial.devices.vex import V5Device
    from pros.serial.ports import DirectPort
    import re
    if not file or os.path.isdir(file):
        import pros.conductor as c
        path = c.Project.find_project(file)
        if path:
            file = f'{c.Project(path).name}.bin'
    elif not re.match(r'[\w\.]{1,24}', file):
        logger(__name__).error('file must be a valid V5 filename')
        return 1
    port = resolve_v5_port(port, 'system')
    ser = DirectPort(port)
    device = V5Device(ser)
    device.execute_program_file(file, run=False)
