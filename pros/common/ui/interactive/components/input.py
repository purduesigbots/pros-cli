from typing import *

from .component import BasicParameterComponent, P


class InputBox(BasicParameterComponent[P], Generic[P]):
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
