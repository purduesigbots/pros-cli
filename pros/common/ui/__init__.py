import threading

import jsonpickle
from click._termui_impl import ProgressBar as _click_ProgressBar
from sentry_sdk import add_breadcrumb

from ..utils import *

_last_notify_value = 0
_current_notify_value = 0
_machine_pickler = jsonpickle.JSONBackend()


def _machineoutput(obj: Dict[str, Any]):
    click.echo(f'Uc&42BWAaQ{jsonpickle.dumps(obj, unpicklable=False, backend=_machine_pickler)}')


def _machine_notify(method: str, obj: Dict[str, Any], notify_value: Optional[int]):
    if notify_value is None:
        global _current_notify_value
        notify_value = _current_notify_value
    obj['type'] = f'notify/{method}'
    obj['notify_value'] = notify_value
    _machineoutput(obj)


def echo(text: Any, err: bool = False, nl: bool = True, notify_value: int = None, color: Any = None,
         output_machine: bool = True, ctx: Optional[click.Context] = None):
    add_breadcrumb(message=text, category='echo')
    if ismachineoutput(ctx):
        if output_machine:
            return _machine_notify('echo', {'text': str(text) + ('\n' if nl else '')}, notify_value)
    else:
        return click.echo(str(text), nl=nl, err=err, color=color)


def confirm(text: str, default: bool = False, abort: bool = False, prompt_suffix: bool = ': ',
            show_default: bool = True, err: bool = False, title: AnyStr = 'Please confirm:',
            log: str = None):
    add_breadcrumb(message=text, category='confirm')
    if ismachineoutput():
        from pros.common.ui.interactive.ConfirmModal import ConfirmModal
        from pros.common.ui.interactive.renderers import MachineOutputRenderer

        app = ConfirmModal(text, abort, title, log)
        rv = MachineOutputRenderer(app).run()
    else:
        rv = click.confirm(text, default=default, abort=abort, prompt_suffix=prompt_suffix,
                           show_default=show_default, err=err)
    add_breadcrumb(message=f'User responded: {rv}')
    return rv


def prompt(text, default=None, hide_input=False,
           confirmation_prompt=False, type=None,
           value_proc=None, prompt_suffix=': ',
           show_default=True, err=False):
    if ismachineoutput():
        # TODO
        pass
    else:
        return click.prompt(text, default=default, hide_input=hide_input, confirmation_prompt=confirmation_prompt,
                            type=type, value_proc=value_proc, prompt_suffix=prompt_suffix, show_default=show_default,
                            err=err)


def progressbar(iterable: Iterable = None, length: int = None, label: str = None, show_eta: bool = True,
                show_percent: bool = True, show_pos: bool = False, item_show_func: Callable = None,
                fill_char: str = '#', empty_char: str = '-', bar_template: str = '%(label)s [%(bar)s] %(info)s',
                info_sep: str = ' ', width: int = 36):
    if ismachineoutput():
        return _MachineOutputProgressBar(**locals())
    else:
        return click.progressbar(**locals())


def finalize(method: str, data: Union[str, Dict, object, List[Union[str, Dict, object, Tuple]]],
             human_prefix: Optional[str] = None):
    """
    To all those who have to debug this... RIP
    """

    if isinstance(data, str):
        human_readable = data
    elif isinstance(data, dict):
        human_readable = data
    elif isinstance(data, List):
        if len(data) == 0:
            human_readable = ''
        elif isinstance(data[0], str):
            human_readable = '\n'.join(data)
        elif isinstance(data[0], dict) or isinstance(data[0], object):
            if hasattr(data[0], '__str__'):
                human_readable = '\n'.join([str(d) for d in data])
            else:
                if not isinstance(data[0], dict):
                    data = [d.__dict__ for d in data]
                import tabulate
                human_readable = tabulate.tabulate([d.values() for d in data], headers=data[0].keys())
        elif isinstance(data[0], tuple):
            import tabulate
            human_readable = tabulate.tabulate(data[1:], headers=data[0])
        else:
            human_readable = data
    elif hasattr(data, '__str__'):
        human_readable = str(data)
    else:
        human_readable = data.__dict__
    human_readable = (human_prefix or '') + str(human_readable)
    if ismachineoutput():
        _machineoutput({
            'type': 'finalize',
            'method': method,
            'data': data,
            'human': human_readable
        })
    else:
        echo(human_readable)


class _MachineOutputProgressBar(_click_ProgressBar):
    def __init__(self, *args, **kwargs):
        global _current_notify_value
        kwargs['file'] = open(os.devnull, 'w', encoding='UTF-8')
        self.notify_value = kwargs.pop('notify_value', _current_notify_value)
        super(_MachineOutputProgressBar, self).__init__(*args, **kwargs)

    def __del__(self):
        self.file.close()

    def render_progress(self):
        super(_MachineOutputProgressBar, self).render_progress()
        obj = {'text': self.label, 'pct': self.pct}
        if self.show_eta and self.eta_known and not self.finished:
            obj['eta'] = self.eta
        _machine_notify('progress', obj, self.notify_value)


class Notification(object):
    def __init__(self, notify_value: Optional[int] = None):
        global _last_notify_value
        if not notify_value:
            notify_value = _last_notify_value + 1
        if notify_value > _last_notify_value:
            _last_notify_value = notify_value
        self.notify_value = notify_value
        self.old_notify_values = []

    def __enter__(self):
        global _current_notify_value
        self.old_notify_values.append(_current_notify_value)
        _current_notify_value = self.notify_value

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _current_notify_value
        _current_notify_value = self.old_notify_values.pop()


class EchoPipe(threading.Thread):
    def __init__(self, err: bool = False, ctx: Optional[click.Context] = None):
        """Setup the object with a logger and a loglevel
        and start the thread
        """
        self.click_ctx = ctx or click.get_current_context(silent=True)
        self.is_err = err
        threading.Thread.__init__(self)
        self.daemon = False
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead, encoding='UTF-8')
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything.
        """
        for line in iter(self.pipeReader.readline, ''):
            echo(line.strip('\n'), ctx=self.click_ctx, err=self.is_err)

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe.
        """
        os.close(self.fdWrite)


__all__ = ['finalize', 'echo', 'confirm', 'prompt', 'progressbar', 'EchoPipe']
