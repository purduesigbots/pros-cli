import logging
import sys
from typing import *

from .ui import confirm, echo
from .utils import get_version

if TYPE_CHECKING:
    from raven import Client  # noqa: F401, flake8 issue with "if TYPE_CHECKING"
    import jsonpickle.handlers  # noqa: F401, flake8 issue, flake8 issue with "if TYPE_CHECKING"
    from pros.config.cli_config import CliConfig  # noqa: F401, flake8 issue, flake8 issue with "if TYPE_CHECKING"

client: Optional['Client'] = None
__excepthook = None  # hook into uncaught exceptions before Sentry gets a hold of them so we can prompt the user
cli_config: 'CliConfig' = None

SUPPRESSED_EXCEPTIONS = [PermissionError]


def prompt_to_send(send: Callable, *args, **kwargs):
    """
    Asks the user for permission to send data to Sentry
    """
    global cli_config
    if cli_config is None or (cli_config.offer_sentry is not None and not cli_config.offer_sentry):
        return
    rv = confirm('We detected something went wrong! '
                 'Would you like to send a bug report to the PROS Development team?',
                 default=True)
    if client:
        # for data we see, this should always be true. But if it's not we have a good indicator that we're not properly
        # catching things before sentry ships data out
        client.extra_context({'explicit_permission': rv})
    if rv:
        echo('Sending report...')
        send(*args, **kwargs)
    if not rv and cli_config.offer_sentry is None:
        cli_config.offer_sentry = confirm('Do you want to continue seeing these prompts? '
                                          'No will disable sending any bug reports.', default=True)
        cli_config.save()


class SentryHandler(logging.Handler):
    """
    Log handler which will send errors to Sentry, with the user's permission
    """

    def __init__(self, client: 'Client', *args, **kwargs):
        self.sentry_client = client
        super().__init__(*args, **kwargs)

    def emit(self, record: logging.LogRecord):
        # record level must be at least logging.ERROR; the sentry attribute (if present) must be true;
        # and if we're logging an exception, it must not be a suppressed exception (execution info implies execution
        # info is not in suppressed exceptions)
        if getattr(record, 'sentry', record.levelno >= logging.ERROR) and \
                (record.exc_info is None or not any(issubclass(record.exc_info[0], e) for e in SUPPRESSED_EXCEPTIONS)):
            def _send():
                if record.exc_info:
                    self.sentry_client.captureException(exc_info=record.exc_info)
                else:
                    self.sentry_client.captureMessage(record.getMessage())

            prompt_to_send(_send)


def add_context(obj: object, override_handlers: bool = True, key: str = None) -> None:
    """
    Adds extra metadata to the sentry log
    :param obj: Any object (non-primitive)
    :param override_handlers: Override some serialization handlers to reduce the output sent to Sentry
    :param key: Name of the object to be inserted into the context, may be None to use the classname of obj
    """
    global client
    if not client:
        return

    import jsonpickle.handlers  # noqa: F811, flake8 issue with "if TYPE_CHECKING"
    from pros.conductor.templates import BaseTemplate

    class TemplateHandler(jsonpickle.handlers.BaseHandler):
        """
        Override how templates get pickled by JSON pickle - we don't want to send all of the data about a template
        from an object
        """
        from pros.conductor.templates import BaseTemplate

        def flatten(self, obj: BaseTemplate, data):
            rv = {
                'name': obj.name,
                'version': obj.version,
                'target': obj.target,
            }
            if hasattr(obj, 'location'):
                rv['location'] = obj.location
            if hasattr(obj, 'origin'):
                rv['origin'] = obj.origin
            return rv

        def restore(self, obj):
            raise NotImplementedError

    if override_handlers:
        jsonpickle.handlers.register(BaseTemplate, TemplateHandler, base=True)

    client.extra_context({
        (key or obj.__class__.__qualname__): jsonpickle.pickler.Pickler(unpicklable=False).flatten(obj)
    })

    if override_handlers:
        jsonpickle.handlers.unregister(BaseTemplate)


def register(cfg: Optional['CliConfig'] = None):
    from raven import Client  # noqa: F811, flake8 issue with "if TYPE_CHECKING"

    global client, __excepthook, cli_config

    if cfg is None:
        from pros.config.cli_config import cli_config as get_cli_config
        cli_config = get_cli_config()
    else:
        cli_config = cfg
    assert cli_config is not None

    if cli_config.offer_sentry is False:
        return

    client = Client('https://00bd27dcded6436cad5c8b2941d6a9d6:e7e9b3eb1ba94951b5079d22b0416627@sentry.io/1226033',
                    install_logging_hook=True,
                    install_sys_hook=True,
                    hook_libraries=['requests'],
                    release=get_version(),
                    tags={
                        'platformv2': 'not yet implemented'
                    })
    _handler = SentryHandler(client)
    logging.getLogger('').addHandler(_handler)

    __excepthook = sys.excepthook

    def handle_exception(*args):
        prompt_to_send(__excepthook, *args)

    sys.excepthook = handle_exception


__all__ = ['add_context', 'register']
