from typing import *

from .component import Component
from ..observable import Observable


class Button(Component, Observable):
    def __init__(self, text: AnyStr):
        super().__init__()
        self.text = text

    def on_clicked(self, *handlers: Callable, **kwargs):
        return self.on('clicked', *handlers, **kwargs)

    def __getstate__(self) -> dict:
        return dict(
            **super(Button, self).__getstate__(),
            text=self.text,
            uuid=self.uuid
        )
