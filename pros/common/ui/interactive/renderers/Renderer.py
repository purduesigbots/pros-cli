from ..application import Application


class Renderer(object):
    def __init__(self, app: Application):
        self.app = app

    def render(self, app: Application) -> None:
        raise NotImplementedError()

    def run(self) -> None:
        raise NotImplementedError()
