import click.core

from pros.common.sentry import add_tag
from pros.common.utils import *
from .click_classes import *


def verbose_option(f: Union[click.Command, Callable]):
    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        if value is None:
            return None
        ctx.ensure_object(dict)
        if isinstance(value, str):
            value = getattr(logging, value.upper(), None)
        if not isinstance(value, int):
            raise ValueError('Invalid log level: {}'.format(value))
        if value:
            logger().setLevel(min(logger().level, logging.INFO))
            stdout_handler = ctx.obj['click_handler']  # type: logging.Handler
            stdout_handler.setLevel(logging.INFO)
            logger(__name__).info('Verbose messages enabled')
        return value

    return click.option('--verbose', help='Enable verbose output', is_flag=True, is_eager=True, expose_value=False,
                        callback=callback, cls=PROSOption, group='Standard Options')(f)


def debug_option(f: Union[click.Command, Callable]):
    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        if value is None:
            return None
        ctx.ensure_object(dict)
        if isinstance(value, str):
            value = getattr(logging, value.upper(), None)
        if not isinstance(value, int):
            raise ValueError('Invalid log level: {}'.format(value))
        if value:
            logging.getLogger().setLevel(logging.DEBUG)
            stdout_handler = ctx.obj['click_handler']  # type: logging.Handler
            stdout_handler.setLevel(logging.DEBUG)
            logging.getLogger(__name__).info('Debugging messages enabled')
        if logger('pros').isEnabledFor(logging.DEBUG):
            logger('pros').debug(f'CLI Version: {get_version()}')
        return value

    return click.option('--debug', help='Enable debugging output', is_flag=True, is_eager=True, expose_value=False,
                        callback=callback, cls=PROSOption, group='Standard Options')(f)


def logging_option(f: Union[click.Command, Callable]):
    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        if value is None:
            return None
        ctx.ensure_object(dict)
        if isinstance(value, str):
            value = getattr(logging, value.upper(), None)
        if not isinstance(value, int):
            raise ValueError('Invalid log level: {}'.format(value))
        logging.getLogger().setLevel(min(logger().level, value))
        stdout_handler = ctx.obj['click_handler']  # type: logging.Handler
        stdout_handler.setLevel(value)
        return value

    return click.option('-l', '--log', help='Logging level', is_eager=True, expose_value=False, callback=callback,
                        type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
                        cls=PROSOption, group='Standard Options')(f)


def logfile_option(f: Union[click.Command, Callable]):
    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        if value is None or value[0] is None:
            return None
        ctx.ensure_object(dict)
        level = None
        if isinstance(value[1], str):
            level = getattr(logging, value[1].upper(), None)
        if not isinstance(level, int):
            raise ValueError('Invalid log level: {}'.format(value[1]))
        handler = logging.FileHandler(value[0], mode='w')
        fmt_str = '%(name)s.%(funcName)s:%(levelname)s - %(asctime)s - %(message)s'
        handler.setFormatter(logging.Formatter(fmt_str))
        handler.setLevel(level)
        logging.getLogger().addHandler(handler)
        stdout_handler = ctx.obj['click_handler']  # type: logging.Handler
        stdout_handler.setLevel(logging.getLogger().level)  # pin stdout_handler to its current log level
        logging.getLogger().setLevel(min(logging.getLogger().level, level))

    return click.option('--logfile', help='Log messages to a file', is_eager=True, expose_value=False,
                        callback=callback, default=(None, None),
                        type=click.Tuple(
                            [click.Path(), click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])]
                        ), cls=PROSOption, group='Standard Options')(f)


def machine_output_option(f: Union[click.Command, Callable]):
    """
    provides a wrapper for creating the machine output option (so don't have to create callback, parameters, etc.)
    """

    def callback(ctx: click.Context, param: click.Parameter, value: str):
        ctx.ensure_object(dict)
        add_tag('machine-output', value)  # goes in sentry report
        if value:
            ctx.obj[param.name] = value
            logging.getLogger().setLevel(logging.DEBUG)
            stdout_handler = ctx.obj['click_handler']  # type: logging.Handler
            stdout_handler.setLevel(logging.DEBUG)
            logging.getLogger(__name__).info('Debugging messages enabled')
        return value

    decorator = click.option('--machine-output', expose_value=False, is_flag=True, default=False, is_eager=True,
                             help='Enable machine friendly output.', callback=callback, cls=PROSOption, hidden=True)(f)
    decorator.__name__ = f.__name__
    return decorator


def default_options(f: Union[click.Command, Callable]):
    """
     combines verbosity, debug, machine output options (most commonly used)
    """
    decorator = debug_option(verbose_option(logging_option(logfile_option(machine_output_option(f)))))
    decorator.__name__ = f.__name__
    return decorator


def template_query(arg_name='query', required: bool = False):
    """
    provides a wrapper for conductor commands which require an optional query

    Ignore unknown options is required in context_settings for the command:
    context_settings={'ignore_unknown_options': True}
    """

    def callback(ctx: click.Context, param: click.Parameter, value: Tuple[str, ...]):
        import pros.conductor as c
        value = list(value)
        spec = None
        if len(value) > 0 and not value[0].startswith('--'):
            spec = value.pop(0)
        if not spec and required:
            raise ValueError(f'A {arg_name} is required to perform this command')
        query = c.BaseTemplate.create_query(spec,
                                            **{value[i][2:]: value[i + 1] for i in
                                               range(0, int(len(value) / 2) * 2, 2)})
        logger(__name__).debug(query)
        return query

    def wrapper(f: Union[click.Command, Callable]):
        return click.argument(arg_name, nargs=-1, required=required, callback=callback)(f)

    return wrapper


def project_option(arg_name='project', required: bool = True, default: str = '.', allow_none: bool = False):
    def callback(ctx: click.Context, param: click.Parameter, value: str):
        if allow_none and value is None:
            return None
        import pros.conductor as c
        project_path = c.Project.find_project(value)
        if project_path is None:
            raise click.UsageError(f'{os.path.abspath(value or ".")} is not inside a PROS project. '
                                   f'Execute this command from within a PROS project or specify it '
                                   f'with --project project/path')
        return c.Project(project_path)

    def wrapper(f: Union[click.Command, Callable]):
        return click.option(f'--{arg_name}', callback=callback, required=required,
                            default=default, type=click.Path(exists=True), show_default=True,
                            help='PROS Project directory or file')(f)

    return wrapper


def shadow_command(command: click.Command):
    def wrapper(f: Union[click.Command, Callable]):
        if isinstance(f, click.Command):
            f.params.extend(p for p in command.params if p.name not in [p.name for p in command.params])
        else:
            if not hasattr(f, '__click_params__'):
                f.__click_params__ = []
            f.__click_params__.extend(p for p in command.params if p.name not in [p.name for p in f.__click_params__])
        return f

    return wrapper


root_commands = []


def pros_root(f):
    decorator = click.group(cls=PROSRoot)(f)
    decorator.__name__ = f.__name__
    root_commands.append(decorator)
    return decorator


def resolve_v5_port(port: Optional[str], type: str, quiet: bool = False) -> Tuple[Optional[str], bool]:
    """
    Detect serial ports that can be used to interact with a V5.

    Returns a tuple of (port?, is_joystick). port will be None if no ports are
    found, and is_joystick is False unless type == 'user' and the port is
    determined to be a controller. This is useful in e.g.
    pros.cli.terminal:terminal where the communication protocol is different for
    wireless interaction.
    """
    from pros.serial.devices.vex import find_v5_ports
    # If a port is specified manually, we'll just assume it's
    # not a joystick.
    is_joystick = False
    if not port:
        ports = find_v5_ports(type)
        if len(ports) == 0:
            if not quiet:
                logger(__name__).error('No {0} ports were found! If you think you have a {0} plugged in, '
                                       'run this command again with the --debug flag'.format('v5'),
                                       extra={'sentry': False})
            return None, False
        if len(ports) > 1:
            if not quiet:
                port = click.prompt('Multiple {} ports were found. Please choose one: '.format('v5'),
                                    default=ports[0].device,
                                    type=click.Choice([p.device for p in ports]))
                assert port in [p.device for p in ports]
            else:
                return None, False
        else:
            port = ports[0].device
            is_joystick = type == 'user' and 'Controller' in ports[0].description
            logger(__name__).info('Automatically selected {}'.format(port))
    return port, is_joystick


def resolve_cortex_port(port: Optional[str], quiet: bool = False) -> Optional[str]:
    from pros.serial.devices.vex import find_cortex_ports
    if not port:
        ports = find_cortex_ports()
        if len(ports) == 0:
            if not quiet:
                logger(__name__).error('No {0} ports were found! If you think you have a {0} plugged in, '
                                       'run this command again with the --debug flag'.format('cortex'),
                                       extra={'sentry': False})
            return None
        if len(ports) > 1:
            if not quiet:
                port = click.prompt('Multiple {} ports were found. Please choose one: '.format('cortex'),
                                    default=ports[0].device,
                                    type=click.Choice([p.device for p in ports]))
                assert port in [p.device for p in ports]
            else:
                return None
        else:
            port = ports[0].device
            logger(__name__).info('Automatically selected {}'.format(port))
    return port
