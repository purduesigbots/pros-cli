import serial.tools.list_ports as list_ports

import pros.conductor as c
from pros.serial.ports import DirectPort
from pros.serial.vex import *
from .click_classes import *
from .common import *


@click.group(cls=PROSGroup)
def upload_cli():
    pass


@upload_cli.command()
@click.option('--target', type=click.Choice(['v5', 'cortex']), default=None, required=False,
              help='Specify the target microcontroller. Overridden when a PROS project is specified.')
@click.argument('path', type=click.Path(exists=True), default=None, required=False)
@click.argument('port', type=str, default=None, required=False)
@click.option('--run-after/--no-run-after', 'run_after', default=True, help='Immediately run the uploaded program')
@click.option('--name', type=str, default=None, required=False, help='Remote program name',
              cls=PROSOption, group='V5 Options')
@click.option('--slot', default=1, show_default=True, type=click.IntRange(min=1, max=8), help='Program slot on the GUI',
              cls=PROSOption, group='V5 Options')
@click.option('--program-version', default=None, type=str, help='Specify version metadata for program',
              cls=PROSOption, group='V5 Options', hidden=True)
@click.option('--icon', default=None, type=str,
              cls=PROSOption, group='V5 Options', hidden=True)
@click.option('--ini-config', type=click.Path(exists=True), default=None, help='Specify a Program Configuration File',
              cls=PROSOption, group='V5 Options', hidden=True)
@default_options
def upload(path: str, port: str, **kwargs):
    """
    Upload a binary to a microcontroller.

    [PATH] may be a directory or file. If a directory, finds a PROS project root and uploads the binary for the correct
    target automatically. If a file, then the file is uploaded. Note that --target must be specified in this case.

    [PORT] may be any valid communication port file, such as COM1 or /dev/ttyACM0. If left blank, then a port is
    automatically detected based on the target (or as supplied by the PROS project)
    """
    args = []
    if path is None or os.path.isdir(path):
        project_path = c.Project.find_project(path or os.getcwd())
        if project_path is None:
            logger(__name__).error('Specify a file to upload or set the cwd inside a PROS project')
            return -1
        project = c.Project(project_path)
        path = project.output
        if project.target == 'v5' and not kwargs['name']:
            kwargs['name'] = project.name

        # apply upload_options as a template
        options = dict(**project.upload_options)
        options.update(kwargs)
        kwargs = options

        kwargs['target'] = project.target  # enforce target because uploading to the wrong uC is VERY bad
        if 'program-version' in kwargs:
            kwargs['version'] = kwargs['program-version']
    if 'name' not in kwargs:
        kwargs['name'] = os.path.basename(path)
    if 'target' not in kwargs:
        raise click.UsageError('Target not specified. specify a project (using the file argument) or target manually')

    if kwargs['target'] == 'v5':
        port = resolve_v5_port(port, 'system')
    elif kwargs['target'] == 'cortex':
        port = resolve_cortex_port(port)
    if not port:
        return -1

    if kwargs['target'] == 'v5':
        if kwargs['name'] is None:
            kwargs['name'] = os.path.splitext(os.path.basename(path))[0]
        args.append(kwargs.pop('name').replace('@', '_'))
        kwargs['slot'] -= 1
    elif kwargs['target'] == 'cortex':
        pass

    # print what was decided
    click.echo('Uploading {} to {} device on {}'.format(path, kwargs['target'], port), nl=False)
    if kwargs['target'] == 'v5':
        click.echo(' as {}'.format(args[0]), nl=False)
    click.echo()

    logger(__name__).debug('Arguments: {}'.format(str(kwargs)))
    if not os.path.isfile(path) and path is not '-':
        logger(__name__).error(
            '{} is not a valid file! Make sure it exists (e.g. by building your project)'.format(path))
        return -1

    # Do the actual uploading!
    try:
        ser = DirectPort(port)
        device = None
        if kwargs['target'] == 'v5':
            device = V5Device(ser)
        elif kwargs['target'] == 'cortex':
            device = CortexDevice(ser)
        with click.open_file(path, mode='rb') as pf:
            device.write_program(pf, *args, **kwargs)
    except Exception as e:
        logger(__name__).debug(e, exc_info=True)
        click.echo(e, err=True)
        exit(1)


def _print_ports(ports, header: Optional[str] = None):
    if header and not ismachineoutput():
        if len(ports) > 0:
            print('{}:'.format(header))
        else:
            print('There are no connected {}'.format(header))
            return
    if ismachineoutput():
        print([{'device': p.device, 'desc': p.description} for p in ports])
    else:
        if isdebug():
            print('\n'.join([str(p.__dict__) for p in ports]))
        else:
            print('\n'.join(['{} - {}'.format(p.device, p.description) for p in ports]))


@upload_cli.command('lsusb', aliases=['ls-usb', 'ls-devices', 'lsdev', 'list-usb', 'list-devices'])
@click.option('--target', type=click.Choice(['v5', 'cortex']), default=None, required=False)
@default_options
def ls_usb(target):
    if target == 'v5' or target is None:
        ports = find_v5_ports('system')
        _print_ports(ports, 'VEX EDR V5 System Ports')

        ports = find_v5_ports('User')
        _print_ports(ports, 'VEX EDR V5 User Ports')
    if target == 'cortex' or target is None:
        ports = find_cortex_ports()
        _print_ports(ports, 'VEX EDR Cortex Microcontroller Ports')

    if isdebug():
        _print_ports(list_ports.comports())
