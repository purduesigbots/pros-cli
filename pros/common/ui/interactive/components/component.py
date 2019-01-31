from typing import *

from pros.common.ui.interactive.parameters.parameter import Parameter
from pros.common.ui.interactive.parameters.validatable_parameter import ValidatableParameter


class Component(object):
    """
    A Component is the basic building block of something to render to users.

    Components must convey type. For backwards compatibility, Components will advertise their class hierarchy to
    the renderer so that it may try to render something reasonable if the renderer hasn't implemented a handler
    for the specific component class.
    For instance, DropDownComponent is a subclass of BasicParameterComponent, ParameterizedComponent, and finally
    Component. If a renderer has not implemented DropDownComponent, then it can render its version of a
    BasicParameterComponent (or ParameterizedComponent). Although a dropdown isn't rendered to the user, something
    reasonable can still be displayed.
    """

    @classmethod
    def get_hierarchy(cls, base: type) -> Optional[List[str]]:
        if base == cls:
            return [base.__name__]
        for t in base.__bases__:
            lst = cls.get_hierarchy(t)
            if lst:
                lst.insert(0, base.__name__)
                return lst
        return None

    def __getstate__(self) -> Dict:
        return dict(
            etype=Component.get_hierarchy(self.__class__)
        )


P = TypeVar('P', bound=Parameter)


class ParameterizedComponent(Component, Generic[P]):
    """
    A ParameterizedComponent has a parameter which takes a value
    """

    def __init__(self, parameter: P):
        self.parameter = parameter

    def __getstate__(self):
        extra_state = {}
        if isinstance(self.parameter, ValidatableParameter):
            extra_state['valid'] = self.parameter.is_valid()
            reason = self.parameter.is_valid_reason()
            if reason:
                extra_state['valid_reason'] = self.parameter.is_valid_reason()
        return dict(
            **super(ParameterizedComponent, self).__getstate__(),
            **extra_state,
            value=self.parameter.value,
            uuid=self.parameter.uuid,
        )


class BasicParameterizedComponent(ParameterizedComponent[P], Generic[P]):
    """
    A BasicParameterComponent is a ParameterizedComponent with a label.
    """

    def __init__(self, label: AnyStr, parameter: P):
        super().__init__(parameter)
        self.label = label

    def __getstate__(self):
        return dict(
            **super(BasicParameterizedComponent, self).__getstate__(),
            text=self.label,
        )
