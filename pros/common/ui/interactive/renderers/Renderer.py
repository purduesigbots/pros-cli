from typing import *

from ..application import Application

P = TypeVar('P')


class Renderer(Generic[P]):
    """
    The Renderer is responsible for:
        - Rendering the application in a manner that is accepted by the presenter
        - Triggering events that the presenter tells us about
        - Returning a value to the callee
    """

    def __init__(self, app: Application[P]):
        self.app = app
        self.run_rv: Any = None

        @app.on_return_set
        def on_return_set(value):
            self.run_rv = value

    def render(self, app: Application[P]) -> None:
        raise NotImplementedError()

    def run(self) -> P:
        raise NotImplementedError()
