import pros.common.ui as ui
import pros.conductor as c

from .click_classes import *
from .common import *


@pros_root
def upload_cli():
    pass


@upload_cli.command(aliases=['u'])
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
    import pros.serial.devices.vex as vex
    from pros.serial.ports import DirectPort
    args = []
    if path is None or os.path.isdir(path):
        project_path = c.Project.find_project(path or os.getcwd())
        if project_path is None:
            logger(__name__).error('Specify a file to upload or set the cwd inside a PROS project')
            return -1
        project = c.Project(project_path)
        path = os.path.join(project.location, project.output)
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
            kwargs['name'] = project.name
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
    ui.echo('Uploading {} to {} device on {}'.format(path, kwargs['target'], port), nl=False)
    if kwargs['target'] == 'v5':
        ui.echo(f' as {args[0]} to slot {kwargs["slot"] + 1}', nl=False)
    ui.echo('')

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
            device = vex.V5Device(ser)
        elif kwargs['target'] == 'cortex':
            device = vex.CortexDevice(ser).get_connected_device()
        with click.open_file(path, mode='rb') as pf:
            device.write_program(pf, *args, **kwargs)
    except Exception as e:
        logger(__name__).exception(e, exc_info=True)
        exit(1)

    ui.finalize('upload', f'Finished uploading {path} to {kwargs["target"]} on {port}')


@upload_cli.command('lsusb', aliases=['ls-usb', 'ls-devices', 'lsdev', 'list-usb', 'list-devices'])
@click.option('--target', type=click.Choice(['v5', 'cortex']), default=None, required=False)
@default_options
def ls_usb(target):
    """
    List plugged in VEX Devices
    """
    from pros.serial.devices.vex import find_v5_ports, find_cortex_ports

    class PortReport(object):
        def __init__(self, header: str, ports: List[Any], machine_header: Optional[str] = None):
            self.header = header
            self.ports = [{'device': p.device, 'desc': p.description} for p in ports]
            self.machine_header = machine_header or header

        def __getstate__(self):
            return {
                'device_type': self.machine_header,
                'devices': self.ports
            }

        def __str__(self):
            if len(self.ports) == 0:
                return f'There are no connected {self.header}'
            else:
                port_str = "\n".join([f"{p['device']} - {p['desc']}" for p in self.ports])
                return f'{self.header}:\n{port_str}'

    result = []
    if target == 'v5' or target is None:
        ports = find_v5_ports('system')
        result.append(PortReport('VEX EDR V5 System Ports', ports, 'v5/system'))

        ports = find_v5_ports('User')
        result.append(PortReport('VEX EDR V5 User ports', ports, 'v5/user'))
    if target == 'cortex' or target is None:
        ports = find_cortex_ports()
        result.append(PortReport('VEX EDR Cortex Microcontroller Ports', ports, 'cortex'))

    ui.finalize('lsusb', result)


@upload_cli.command('upload-terminal', aliases=['ut'], hidden=True)
@click.pass_context
def make_upload_terminal(ctx):
    from .terminal import terminal
    ctx.forward(upload)
    ctx.forward(terminal, request_banner=False)
