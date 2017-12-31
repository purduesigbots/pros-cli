import logging
import sys
from functools import wraps
from typing import *
import os

import click

import pros


def get_version():
    try:
        ver = open(os.path.join(os.path.dirname(__file__), '..', 'version')).read().strip()
        if ver is not None:
            return ver
    except:
        pass
    try:
        if getattr(sys, 'frozen', False):
            import BUILD_CONSTANTS
            ver = BUILD_CONSTANTS.CLI_VERSION
            if ver is not None:
                return ver
    except:
        pass
    try:
        import pkg_resources
    except ImportError:
        pass
    else:
        module = sys._getframe(1).f_globals.get('__name__')
        for dist in pkg_resources.working_set:
            scripts = dist.get_entry_map().get('console_scripts') or {}
            for script_name, entry_point in iter(scripts.items()):
                if entry_point.module_name == module:
                    ver = dist.version
                    if ver is not None:
                        return ver
    raise RuntimeError('Could not determine version')


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


def logger(obj: Union[str, object] = pros.__name__) -> logging.Logger:
    if isinstance(obj, str):
        return logging.getLogger(obj)
    return logging.getLogger(obj.__module__)


def get_pros_dir():
    return click.get_app_dir('PROS')
