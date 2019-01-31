import json
from threading import Semaphore, current_thread
from typing import *

import click

from pros.common import ui
from pros.common.ui.interactive.observable import Observable
from .Renderer import Renderer
from ..application import Application

current: List['MachineOutputRenderer'] = []


def _push_renderer(renderer: 'MachineOutputRenderer'):
    global current

    stack: List['MachineOutputRenderer'] = current
    stack.append(renderer)


def _remove_renderer(renderer: 'MachineOutputRenderer'):
    global current

    stack: List['MachineOutputRenderer'] = current
    if renderer in stack:
        stack.remove(renderer)


def _current_renderer() -> Optional['MachineOutputRenderer']:
    global current

    stack: List['MachineOutputRenderer'] = current
    return stack[-1] if len(stack) > 0 else None


P = TypeVar('P')


class MachineOutputRenderer(Renderer[P], Generic[P]):
    def __init__(self, app: Application[P]):
        global current

        super().__init__(app)
        self.alive = False
        self.thread = None
        self.stop_sem = Semaphore(0)

        @app.on_redraw
        def on_redraw():
            self.render(self.app)

        app.on_exit(lambda: self.stop())

    @staticmethod
    def get_line():
        line = click.get_text_stream('stdin').readline().strip()
        return line.strip() if line is not None else None

    def run(self) -> P:
        _push_renderer(self)
        self.thread = current_thread()
        self.alive = True
        while self.alive:
            self.render(self.app)
            if not self.alive:
                break

            line = self.get_line()
            if not self.alive or not line or line.isspace():
                continue

            try:
                value = json.loads(line)
                if 'uuid' in value and 'event' in value:
                    Observable.notify(value['uuid'], value['event'], *value.get('args', []), **value.get('kwargs', {}))
            except json.JSONDecodeError as e:
                ui.logger(__name__).exception(e)
            except BaseException as e:
                ui.logger(__name__).exception(e)
                break
        self.stop_sem.release()
        self.stop()
        return self.run_rv

    def stop(self):
        ui.logger(__name__).debug(f'Stopping {self.app}')
        self.alive = False

        if current_thread() != self.thread:
            ui.logger(__name__).debug(f'Interrupting render thread of {self.app}')
            while not self.stop_sem.acquire(timeout=0.1):
                self.wake_me()

        ui.logger(__name__).debug(f'Broadcasting stop {self.app}')
        self._output({
            'uuid': self.app.uuid,
            'should_exit': True
        })

        _remove_renderer(self)
        top_renderer = _current_renderer()
        if top_renderer:
            top_renderer.wake_me()

    def wake_me(self):
        """
        Hack to wake up input thread to know to shut down
        """
        ui.logger(__name__).debug(f'Broadcasting WAKEME for {self.app}')
        if ui.ismachineoutput():
            ui._machineoutput({'type': 'wakeme'})
        else:
            ui.echo('Wake up the renderer!')

    @staticmethod
    def _output(data: dict):
        data['type'] = 'input/interactive'
        if ui.ismachineoutput():
            ui._machineoutput(data)
        else:
            ui.echo(str(data))

    def render(self, app: Application) -> None:
        if self.alive:
            self._output(app.__getstate__())
