import logging
import os
import os.path
import sys
from functools import lru_cache, wraps
from typing import *

import click

import pros


@lru_cache(1)
def get_version():
    try:
        ver = open(os.path.join(os.path.dirname(__file__), '..', '..', 'version')).read().strip()
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
        import pros.cli.main
        module = pros.cli.main.__name__
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


def isdebug(obj: Union[str, object] = pros.__name__) -> bool:
    if obj is None:
        obj = pros.__name__
    if isinstance(obj, str):
        return logging.getLogger(obj).getEffectiveLevel() == logging.DEBUG
    return logging.getLogger(obj.__module__).getEffectiveLevel() == logging.DEBUG


def ismachineoutput(ctx: click.Context = None) -> bool:
    if ctx is None:
        ctx = click.get_current_context(silent=True)
    if isinstance(ctx, click.Context):
        ctx.ensure_object(dict)
        assert isinstance(ctx.obj, dict)
        return ctx.obj.get('machine_output', False)
    else:
        return False


def get_pros_dir():
    return click.get_app_dir('PROS')


def with_click_context(func):
    ctx = click.get_current_context(silent=True)
    if not ctx or not isinstance(ctx, click.Context):
        return func
    else:
        def _wrap(*args, **kwargs):
            with ctx:
                try:
                    return func(*args, **kwargs)
                except BaseException as e:
                    logger(__name__).exception(e)

        return _wrap


def download_file(url: str, ext: Optional[str] = None, desc: Optional[str] = None) -> Optional[str]:
    """
    Helper method to download a temporary file.
    :param url: URL of the file to download
    :param ext: Expected extension of the file to be downloaded
    :param desc: Description of file being downloaded (for progressbar)
    :return: The path of the downloaded file, or None if there was an error
    """
    import requests
    from pros.common.ui import progressbar
    from rfc6266_parser import parse_requests_response

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filename: str = url.rsplit('/', 1)[-1]
        if 'Content-Disposition' in response.headers.keys():
            try:
                disposition = parse_requests_response(response)
                if isinstance(ext, str):
                    filename = disposition.filename_sanitized(ext)
                else:
                    filename = disposition.filename_unsafe
            except RuntimeError:
                pass
        output_path = os.path.join(get_pros_dir(), 'download', filename)

        if os.path.exists(output_path):
            os.remove(output_path)
        elif not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, mode='wb') as file:
            with progressbar(length=int(response.headers['Content-Length']),
                             label=desc or f'Downloading {filename}') as pb:
                for chunk in response.iter_content(256):
                    file.write(chunk)
                    pb.update(len(chunk))
        return output_path
    return None


def dont_send(e: Exception):
    e.sentry = False
    return e
