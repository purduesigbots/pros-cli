import json
import sys
import threading
import time
from queue import Queue, Empty

from pros.common import ui
from pros.common.ui.interactive.observable import Observable

from .Renderer import Renderer
from ..application import Application


class MachineOutputRenderer(Renderer):
    def __init__(self, app: Application):
        super().__init__(app)
        self.reader_thread = threading.Thread(target=self.reader, name='machine-renderer-input')
        self.alive = threading.Event()

        self.have_sigint = False

        self.q = Queue()
        self.require_redraw = False

        app.on_redraw(self.redraw)

    def redraw(self):
        self.require_redraw = True

    def reader(self):
        try:
            line = ''
            while not self.alive.is_set():
                try:
                    c = sys.stdin.read(1)
                except KeyboardInterrupt:
                    c = '\x03'
                if self.alive.is_set():
                    break
                elif c == '\x03' or self.have_sigint:
                    self.stop()
                    break
                elif c == '\n' or c == '\r':
                    if line:
                        try:
                            self.q.put(json.loads(line.strip()))
                        except json.JSONDecodeError as e:
                            ui.logger(__name__).exception(e)
                        finally:
                            line = ''
                else:
                    line += c
        except Exception as e:
            if not self.alive.is_set():
                ui.logger(__name__).exception(e)
            else:
                ui.logger(__name__).debug(e)
        ui.logger(__name__).info('App reader dying')

    def stop(self):
        if not self.alive.is_set():
            ui.logger(__name__).warning('Stopping interactive application')
            self._output({
                'uuid': self.app.uuid,
                'should_exit': True
            })
            self.alive.set()
            ui.logger(__name__).info('All done!')

    def run(self) -> None:
        self.reader_thread.start()
        while not self.alive.is_set():
            if self.require_redraw:
                self.render(self.app)
                self.require_redraw = False
            try:
                value = self.q.get(block=False)

                if 'uuid' in value and 'event' in value:
                    Observable.notify(value['uuid'], value['event'], *value.get('args', []), **value.get('kwargs', {}))
                    self.redraw()

            except Empty:
                time.sleep(0.1)
        self.stop()

    @staticmethod
    def _output(data: dict):
        data['type'] = 'input/interactive'
        if ui.ismachineoutput():
            ui._machineoutput(data)
        else:
            ui.echo(str(data))

    def render(self, app: Application) -> None:
        self._output(app.__getstate__())
