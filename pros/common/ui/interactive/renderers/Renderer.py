from typing import *

from ..application import Application


class Renderer(object):
    def __init__(self, app: Application):
        self.app = app
        self.run_rv: Any = None

        @app.on_return_set
        def on_return_set(value):
            self.run_rv = value

    def render(self, app: Application) -> None:
        raise NotImplementedError()

    def run(self) -> Any:
        raise NotImplementedError()
