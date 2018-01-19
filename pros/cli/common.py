import click.core

from pros.common.utils import *
from pros.serial.vex import find_cortex_ports, find_v5_ports
from .click_classes import *


def verbose_option(f):
    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        if value is None:
            return None
        ctx.ensure_object(dict)
        if isinstance(value, str):
            value = getattr(logging, value.upper(), None)
        if not isinstance(value, int):
            raise ValueError('Invalid log level: {}'.format(value))
        if value:
            logger().setLevel(logging.INFO)
            stdout_handler = ctx.obj['click_handler']  # type: logging.Handler
            stdout_handler.setLevel(logging.INFO)
            logger(__name__).info('Verbose messages enabled')
        return value

    return click.option('--verbose', help='Enable verbose output', is_flag=True, is_eager=True, expose_value=False,
                        callback=callback, cls=PROSOption, group='Standard Options')(f)


def debug_option(f):
    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        if value is None:
            return None
        ctx.ensure_object(dict)
        if isinstance(value, str):
            value = getattr(logging, value.upper(), None)
        if not isinstance(value, int):
            raise ValueError('Invalid log level: {}'.format(value))
        if value:
            logger().setLevel(logging.DEBUG)
            stdout_handler = ctx.obj['click_handler']  # type: logging.Handler
            stdout_handler.setLevel(logging.DEBUG)
            logger(__name__).info('Debugging messages enabled')
        return value

    return click.option('--debug', help='Enable debugging output', is_flag=True, is_eager=True, expose_value=False,
                        callback=callback, cls=PROSOption, group='Standard Options')(f)


def logging_option(f):
    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        if value is None:
            return None
        ctx.ensure_object(dict)
        if isinstance(value, str):
            value = getattr(logging, value.upper(), None)
        if not isinstance(value, int):
            raise ValueError('Invalid log level: {}'.format(value))
        logger().setLevel(value)
        stdout_handler = ctx.obj['click_handler']  # type: logging.Handler
        stdout_handler.setLevel(value)
        return value

    return click.option('-l', '--log', help='Logging level', is_eager=True, expose_value=False, callback=callback,
                        type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
                        cls=PROSOption, group='Standard Options')(f)


def logfile_option(f):
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
        logger().addHandler(handler)
        logger().setLevel(min(logger().level, level))

    return click.option('--logfile', help='Log messages to a file', is_eager=True, expose_value=False,
                        callback=callback, default=(None, None),
                        type=click.Tuple(
                            [click.Path(), click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])]
                        ), cls=PROSOption, group='Standard Options')(f)


def machine_output_option(f):
    """
    provides a wrapper for creating the machine output option (so don't have to create callback, parameters, etc.)
    """

    def callback(ctx, param, value):
        ctx.ensure_object(dict)
        ctx.obj[param.name] = value
        return value

    decorator = click.option('--machine-output', expose_value=False, is_flag=True, default=False, is_eager=True,
                             help='Enable machine friendly output.', callback=callback, cls=PROSOption, hidden=True)(f)
    decorator.__name__ = f.__name__
    return decorator


def default_options(f):
    """
     combines verbosity, debug, machine output options (most commonly used)
    """
    decorator = debug_option(verbose_option(logging_option(logfile_option(machine_output_option(f)))))
    decorator.__name__ = f.__name__
    return decorator


def resolve_v5_port(port: str, type: str) -> Optional[str]:
    if not port:
        ports = find_v5_ports(type)
        if len(ports) == 0:
            logger(__name__).error('No {0} ports were found! If you think you have a {0} plugged in, '
                                   'run this command again with the --debug flag'.format('v5'))
            return None
        if len(ports) > 1:
            port = click.prompt('Multiple {} ports were found. Please choose one: '.format('v5'),
                                default=ports[0].device,
                                type=click.Choice([p.device for p in ports]))
            assert port in [p.device for p in ports]
        else:
            port = ports[0].device
            logger(__name__).info('Automatically selected {}'.format(port))
    return port


def resolve_cortex_port(port: str) -> Optional[str]:
    if not port:
        ports = find_cortex_ports()
        if len(ports) == 0:
            logger(__name__).error('No {0} ports were found! If you think you have a {0} plugged in, '
                                   'run this command again with the --debug flag'.format('cortex'))
            return None
        if len(ports) > 1:
            port = click.prompt('Multiple {} ports were found. Please choose one: '.format('cortex'),
                                default=ports[0].device,
                                type=click.Choice([p.device for p in ports]))
            assert port in [p.device for p in ports]
        else:
            port = ports[0].device
            logger(__name__).info('Automatically selected {}'.format(port))
    return port
