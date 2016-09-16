import click
from proscli.state import State

pass_state = click.make_pass_decorator(State)


def verbosity_option(f):
    """
    provides a wrapper for creating the verbosity option (so don't have to create callback, parameters, etc.)
    """
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.verbosity += value
        return value
    return click.option('-v', '--verbose', count=True, expose_value=False, help='Enable verbosity level.',
                        is_eager=True, callback=callback)(f)


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
    return click.option('-d', '--debug', expose_value=False, is_flag=True, default=False, is_eager=True,
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
    decorator = click.option('--machine-output', expose_value=False, is_flag=True, default=False, is_eager=True,
                        help='Enable machine friendly output.', callback=callback)(f)
    decorator.__name__ = f.__name__
    return decorator


def default_options(f):
    """
     combines verbosity, debug, machine output options (most commonly used)
    """
    decorator = verbosity_option(debug_option(machine_output_option(f)))
    decorator.__name__ = f.__name__
    return decorator


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
            try:
                ctx = click.get_current_context()
            except Exception:
                ctx = State()
            if ctx is not None and isinstance(ctx, click.Context):
                ctx = ctx.obj
            else:
                ctx = State()
        debug_flag = ctx.debug

    if debug_flag:
        click.echo('\tDEBUG: {}'.format(content))


def verbose(content, level: int = 1, ctx=None):
    if ctx is None:
        try:
            ctx = click.get_current_context()
        except Exception:
            ctx = State()
    if ctx is not None and isinstance(ctx, click.Context):
        ctx = ctx.obj
    elif not isinstance(ctx, State):
        ctx = State()

    if ctx.verbosity >= level:
        click.echo(content)


class AliasGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super(AliasGroup, self).__init__(*args, **kwargs)
        self.cmd_dict = dict()

    def command(self, *args, aliases=[], **kwargs):
        def decorator(f):
            for alias in aliases:
                self.cmd_dict[alias] = f.__name__ if len(args) == 0 else args[0]
            cmd = super(AliasGroup, self).command(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd
        return decorator

    def group(self, aliases=None, *args, **kwargs):
        def decorator(f):
            for alias in aliases:
                self.cmd_dict[alias] = f.__name__
            cmd = super(AliasGroup, self).group(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd
        return decorator

    def get_command(self, ctx, cmd_name):
        # return super(AliasGroup, self).get_command(ctx, cmd_name)
        suggestion = super(AliasGroup, self).get_command(ctx, cmd_name)
        if suggestion is not None:
            return suggestion
        if cmd_name in self.cmd_dict:
            return super(AliasGroup, self).get_command(ctx, self.cmd_dict[cmd_name])
        return None

