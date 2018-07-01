import logging

import click
import jsonpickle

from pros.common import isdebug

_machine_pickler = jsonpickle.JSONBackend()


class PROSLogHandler(logging.StreamHandler):
    """
    A subclass of logging.StreamHandler so that we can correctly encapsulate logging messages
    """

    def __init__(self, *args, ctx_obj=None, **kwargs):
        # Need access to the raw ctx_obj in case an exception is thrown before the context has
        # been initialized (e.g. when argument parsing is happening)
        self.ctx_obj = ctx_obj
        super().__init__(*args, **kwargs)

    def emit(self, record):
        try:
            if self.ctx_obj.get('machine_output', False):
                formatter = self.formatter or logging.Formatter()
                record.message = record.getMessage()
                obj = {
                    'type': 'log/message',
                    'level': record.levelname,
                    'message': formatter.formatMessage(record),
                    'simpleMessage': record.message
                }
                if record.exc_info:
                    obj['trace'] = formatter.formatException(record.exc_info)
                msg = f'Uc&42BWAaQ{jsonpickle.dumps(obj, unpicklable=False, backend=_machine_pickler)}'
            else:
                msg = self.format(record)
            click.echo(msg)
        except Exception:
            self.handleError(record)


class PROSLogFormatter(logging.Formatter):
    """
    A subclass of the logging.Formatter so that we can print full exception traces ONLY if we're in debug mode
    """

    def formatException(self, ei):
        if not isdebug():
            return '\n'.join(super().formatException(ei).split('\n')[-3:])
        else:
            return super().formatException(ei)
