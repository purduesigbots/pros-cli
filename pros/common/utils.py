import logging
from functools import wraps
from typing import *

import click

from pros.common.state import State


def isdebug(state=None):
    if state is None:
        ctx = click.get_current_context(silent=True)
        if ctx is not None and isinstance(ctx, click.Context):
            state = ctx.find_object(State)
        if state is None or not isinstance(state, State):
            state = State()
    assert (state is not None)
    return state.debug


def debug(content, state=None, debug_flag=None):
    if debug_flag is None:
        debug_flag = isdebug(state)

    if debug_flag:
        click.echo('\tDEBUG: {}'.format(content))


def retries(func, retry: int = 3):
    @wraps(func)
    def retries_wrapper(*args, n_retries: int = retry, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if n_retries > 0:
                return retries_wrapper(*args, n_retries=n_retries - 1, **kwargs)
            else:
                raise e

    return retries_wrapper


def logger(obj: Union[str, object]) -> logging.Logger:
    if isinstance(obj, str):
        return logging.getLogger(obj)
    return logging.getLogger(obj.__module__)
