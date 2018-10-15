import json
from json import JSONDecodeError

from click import Abort
from click.termui import visible_prompt_func

import pros.common.ui as ui
from pros.common.ui.interactive.observable import Observable
from .application import Application
from pros.serial.terminal.console import Console


class Renderer(object):
    def render(self, app: Application) -> None:
        raise NotImplementedError()

    def run(self, app: Application) -> None:
        raise NotImplementedError()


class MachineOutputRenderer(Renderer):
    def run(self, app: Application) -> None:
        import threading
        import signal

        alive: threading.Event = threading.Event()
        signal.signal(signal.SIGINT, lambda *_: alive.set())  # SIGINT handler
        console = Console()

        require_redraw = True

        @app.on_exit
        def kill():
            nonlocal alive
            alive.set()
            console.cancel()
            self._output({
                'uuid': app.uuid,
                'should_exit': True
            })

        @app.on_redraw
        def require_redraw():
            nonlocal require_redraw
            require_redraw = True

        import queue
        import time

        q = queue.Queue()

        def reader():
            nonlocal alive
            try:
                line = ''
                while not alive.is_set():
                    c = console.getkey()
                    if not c:
                        continue
                    if c == '\x03':
                        break
                    elif c == '\n':
                        try:
                            q.put(json.loads(line.strip()))
                        except JSONDecodeError as e:
                            ui.logger(__name__).exception(e)
                        finally:
                            line = ''
                    else:
                        line += c
            except (KeyboardInterrupt, EOFError):
                pass
            alive.set()

        input_thread = threading.Thread(target=reader)
        input_thread.start()

        while not alive.is_set():
            if require_redraw:
                self.render(app)
                require_redraw = False
            try:
                value = q.get(block=False)

                if 'uuid' in value and 'event' in value:
                    Observable.notify(value['uuid'], value['event'], *value.get('args', []), **value.get('kwargs', {}))
                require_redraw = True
            except queue.Empty:
                time.sleep(0.1)
        with ui.Notification():
            if input_thread.is_alive():
                console.cancel()
                input_thread.join()

    @staticmethod
    def _output(data: dict):
        data['type'] = 'input/interactive'
        if ui.ismachineoutput():
            ui._machineoutput(data)
        else:
            ui.echo(str(data))

    def render(self, app: Application) -> None:
        self._output(app.__getstate__())
