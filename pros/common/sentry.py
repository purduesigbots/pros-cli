from typing import *

import click

import pros.common.ui as ui

if TYPE_CHECKING:
    from sentry_sdk import Client, Hub, Scope  # noqa: F401, flake8 issue with "if TYPE_CHECKING"
    import jsonpickle.handlers  # noqa: F401, flake8 issue, flake8 issue with "if TYPE_CHECKING"
    from pros.config.cli_config import CliConfig  # noqa: F401, flake8 issue, flake8 issue with "if TYPE_CHECKING"

cli_config: 'CliConfig' = None

SUPPRESSED_EXCEPTIONS = [PermissionError, click.Abort]


def prompt_to_send(event: Dict[str, Any], hint: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Asks the user for permission to send data to Sentry
    """
    global cli_config
    with ui.Notification():
        if cli_config is None or (cli_config.offer_sentry is not None and not cli_config.offer_sentry):
            return

        if 'extra' in event and not event['extra'].get('sentry', True):
            ui.logger(__name__).debug('Not sending candidate event because event was tagged with extra.sentry = False')
            return
        if 'exc_info' in hint and (not getattr(hint['exc_info'][1], 'sentry', True) or
                                   any(isinstance(hint['exc_info'][1], t) for t in SUPPRESSED_EXCEPTIONS)):
            ui.logger(__name__).debug('Not sending candidate event because exception was tagged with sentry = False')
            return

        if not event['tags']:
            event['tags'] = dict()

        extra_text = ''
        if 'message' in event:
            extra_text += event['message'] + '\n'
        if 'culprit' in event:
            extra_text += event['culprit'] + '\n'
        if 'logentry' in event and 'message' in event['logentry']:
            extra_text += event['logentry']['message'] + '\n'
        if 'exc_info' in hint:
            import traceback
            extra_text += ''.join(traceback.format_exception(*hint['exc_info'], limit=4))

        event['tags']['confirmed'] = ui.confirm('We detected something went wrong! Do you want to send a report?',
                                                log=extra_text)
        if event['tags']['confirmed']:
            ui.echo('Sending bug report.')

            ui.echo(f'Want to get updates? Visit https://pros.cs.purdue.edu/report.html?event={event["event_id"]}')
            return event
        else:
            ui.echo('Not sending bug report.')


def add_context(obj: object, override_handlers: bool = True, key: str = None) -> None:
    """
    Adds extra metadata to the sentry log
    :param obj: Any object (non-primitive)
    :param override_handlers: Override some serialization handlers to reduce the output sent to Sentry
    :param key: Name of the object to be inserted into the context, may be None to use the classname of obj
    """

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

    from sentry_sdk import configure_scope
    with configure_scope() as scope:
        scope.set_extra((key or obj.__class__.__qualname__), jsonpickle.pickler.Pickler(unpicklable=False).flatten(obj))

    if override_handlers:
        jsonpickle.handlers.unregister(BaseTemplate)


def add_tag(key: str, value: str):
    from sentry_sdk import configure_scope

    with configure_scope() as scope:
        scope.set_tag(key, value)


def register(cfg: Optional['CliConfig'] = None):
    global cli_config, client

    if cfg is None:
        from pros.config.cli_config import cli_config as get_cli_config
        cli_config = get_cli_config()
    else:
        cli_config = cfg

    assert cli_config is not None

    if cli_config.offer_sentry is False:
        return

    import sentry_sdk as sentry
    from pros.upgrade import get_platformv2

    client = sentry.Client(
        'https://00bd27dcded6436cad5c8b2941d6a9d6@sentry.io/1226033',
        before_send=prompt_to_send,
        release=ui.get_version()
    )
    sentry.Hub.current.bind_client(client)

    with sentry.configure_scope() as scope:
        scope.set_tag('platformv2', get_platformv2().name)


__all__ = ['add_context', 'register', 'add_tag']
