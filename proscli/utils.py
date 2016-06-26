import click
import prosconfig

class State(object):
    def __init__(self):
        self.verbosity = 0
        self.debug = False
        self.machine_output = False
        self.log_key = 'purdueros-logging'
        self.proj_cfg = prosconfig.ProsConfig()

pass_state = click.make_pass_decorator(State, ensure=True)


def verbosity_option(f):
    """
    provides a wrapper for creating the verbosity option (so don't have to create callback, parameters, etc.)
    """
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.verbosity += value
        return value
    return click.option('-v', '--verbose', count=True, expose_value=False, help='Enable verbosity level.',
                        callback=callback)(f)


def debug_option(f):
    """
    provides a wrapper for creating the debug option (so don't have to create callback, parameters, etc.)
    """
    def callback(ctx, param, value):
        if not value:
            return
        state = ctx.ensure_object(State)
        state.debug = value
        return value
    return click.option('-d', '--debug', expose_value=False, is_flag=True, default=False,
                        help='Enable debugging output.', callback=callback)(f)


def machine_output_option(f):
    """
    provides a wrapper for creating the machine output option (so don't have to create callback, parameters, etc.)
    """
    def callback(ctx, param, value):
        if not value:
            return
        state = ctx.ensure_object(State)
        state.machine_output = value
        return value
    return click.option('--machine-output', expose_value=False, is_flag=True, default=False,
                        help='Enable machine friendly output.', callback=callback)(f)


def default_options(f):
    """
     combines verbosity, debug, machine output options (most commonly used)
    """
    return verbosity_option(debug_option(machine_output_option(f)))


def default_cfg(f):
    """
    combines default options and passes the state object
    :param f:
    :return:
    """
    return pass_state(default_options(f))


def debug(content, ctx=None, debug_flag=None):
    if debug_flag is None:
        if ctx is None:
            ctx = click.get_current_context()
            if ctx is not None and isinstance(ctx.obj, State):
                ctx = ctx.obj
            else:
                ctx = State()
        debug_flag = ctx.debug

    if debug_flag:
        click.echo('\tDEBUG: {}'.format(content))

