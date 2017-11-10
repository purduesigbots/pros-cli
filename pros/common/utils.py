import click
from pros.common.state import State

def isdebug(state=None):
    if state is None:
        ctx = click.get_current_context(silent=True)
        if ctx is not None and isinstance(ctx, click.Context):
            state = ctx.find_object(State)
        if state is None or not isinstance(state, State):
            state = State()
    assert(state is not None)
    return state.debug


def debug(content, state=None, debug_flag=None):
    if debug_flag is None:
        debug_flag = isdebug(state)

    if debug_flag:
        click.echo('\tDEBUG: {}'.format(content))