from typing import *

from .component import BasicParameterizedComponent, P


class InputBox(BasicParameterizedComponent[P], Generic[P]):
    """
    An InputBox is a Component with a Parameter that is rendered with an input box
    """

    def __init__(self, label: AnyStr, parameter: P, placeholder: Optional = None):
        super(InputBox, self).__init__(label, parameter)
        self.placeholder = placeholder

    def __getstate__(self) -> dict:
        extra_state = {}
        if self.placeholder is not None:
            extra_state['placeholder'] = self.placeholder
        return dict(
            **super(InputBox, self).__getstate__(),
            **extra_state,
        )


class FileSelector(InputBox[P], Generic[P]):
    pass


class DirectorySelector(InputBox[P], Generic[P]):
    pass
