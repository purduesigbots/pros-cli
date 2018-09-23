import json
from json import JSONDecodeError

from click import Abort
from click.termui import visible_prompt_func

import pros.common.ui as ui
from pros.common.ui.interactive.observable import Observable
from .application import Application


class Renderer(object):
    def render(self, app: Application) -> None:
        raise NotImplementedError()

    def run(self, app: Application) -> None:
        raise NotImplementedError()


class MachineOutputRenderer(Renderer):
    def run(self, app: Application) -> None:
        running = True
        require_redraw = True

        @app.on_exit
        def kill():
            nonlocal running
            running = False

        @app.on_redraw
        def require_redraw():
            nonlocal require_redraw
            require_redraw = True

        import threading
        import queue
        import time

        q = queue.Queue()

        def reader():
            # noinspection PyUnreachableCode
            try:
                while True:
                    try:
                        q.put(json.loads(visible_prompt_func('').strip()))
                    except JSONDecodeError as e:
                        ui.logger(__name__).exception(e)
            except EOFError:
                running = False

        input_thread = threading.Thread(target=reader)
        input_thread.start()

        while running:
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
            except (KeyboardInterrupt, EOFError):
                input_thread.join()
                raise Abort()
            except JSONDecodeError as e:
                ui.logger(__name__).exception(e)
                continue
        input_thread.join()

    def render(self, app: Application) -> None:
        if ui.ismachineoutput():
            ui._machineoutput(dict(
                type='input/interactive',
                **app.__getstate__()
            ))
        else:
            ui.echo(str(dict(
                type='input/interactive',
                **app.__getstate__()
            )))
