from typing import *

from .component import Component


class Label(Component):
    def __init__(self, text: AnyStr):
        self.text = text

    def __getstate__(self):
        return dict(
            **super(Label, self).__getstate__(),
            text=self.text
        )
