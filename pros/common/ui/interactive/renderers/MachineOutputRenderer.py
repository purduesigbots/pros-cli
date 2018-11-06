import json
import sys

from pros.common import ui
from pros.common.ui.interactive.observable import Observable
from typing import *

from .Renderer import Renderer
from ..application import Application


class MachineOutputRenderer(Renderer):
    def __init__(self, app: Application):
        super().__init__(app)
        self.alive = False

        @app.on_redraw
        def on_redraw():
            self.render(self.app)

        app.on_exit(lambda: self.stop())

    def run(self) -> Any:
        self.alive = True
        while self.alive:
            self.render(self.app)
            if not self.alive:
                break
            line = sys.stdin.readline()
            if line.strip().isspace():
                continue
            try:
                value = json.loads(line.strip())
                if 'uuid' in value and 'event' in value:
                    Observable.notify(value['uuid'], value['event'], *value.get('args', []), **value.get('kwargs', {}))
            except json.JSONDecodeError as e:
                ui.logger(__name__).exception(e)
        return self.run_rv

    def stop(self):
        self._output({
            'uuid': self.app.uuid,
            'should_exit': True
        })
        self.alive = False
        ui.logger(__name__).info('All done!')

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
