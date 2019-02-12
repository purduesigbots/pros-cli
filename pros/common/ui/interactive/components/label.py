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


class VerbatimLabel(Label):
    """
    Should be displayed with a monospace font
    """
    pass


class Spinner(Label):
    """
    Spinner is a component which indicates to the user that something is happening in the background
    """

    def __init__(self):
        super(Spinner, self).__init__('Loading...')
