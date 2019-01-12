from typing import *

from pros.common.ui.interactive.parameters import BooleanParameter
from .component import Component


class Container(Component):
    """
    A Container has multiple Components, possibly a title, and possibly a description
    """

    def __init__(self, *elements: Component,
                 title: Optional[AnyStr] = None, description: Optional[AnyStr] = None,
                 collapsed: Union[BooleanParameter, bool] = False):
        self.title = title
        self.description = description
        self.elements = elements
        self.collapsed = BooleanParameter(collapsed) if isinstance(collapsed, bool) else collapsed

    def __getstate__(self):
        extra_state = {
            'uuid': self.collapsed.uuid,
            'collapsed': self.collapsed.value
        }
        if self.title is not None:
            extra_state['title'] = self.title
        if self.description is not None:
            extra_state['description'] = self.description
        return dict(
            **super(Container, self).__getstate__(),
            **extra_state,
            elements=[e.__getstate__() for e in self.elements]
        )
