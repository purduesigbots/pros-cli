from typing import *

from pros.common.ui.interactive.parameters.validatable_parameter import ValidatableParameter
from pros.common.ui.interactive.parameters.parameter import Parameter


class Component(object):
    @classmethod
    def get_hierarchy(cls, base: type) -> Optional[List[str]]:
        if base == cls:
            return [base.__name__]
        for t in base.__bases__:
            l = cls.get_hierarchy(t)
            if l:
                l.insert(0, base.__name__)
                return l
        return None

    def __getstate__(self) -> Dict:
        return dict(
            type=Component.get_hierarchy(self.__class__)
        )


P = TypeVar('P', bound=Parameter)


class ParameterizedComponent(Component, Generic[P]):
    def __init__(self, parameter: P):
        self.parameter = parameter

    def __getstate__(self):
        extra_state = {}
        if isinstance(self.parameter, ValidatableParameter):
            extra_state['valid'] = self.parameter.is_valid()
        return dict(
            **super(ParameterizedComponent, self).__getstate__(),
            **extra_state,
            value=self.parameter.value,
            uuid=self.parameter.uuid,
        )


class BasicParameterComponent(ParameterizedComponent[P], Generic[P]):
    def __init__(self, label: AnyStr, parameter: P):
        super().__init__(parameter)
        self.label = label

    def __getstate__(self):
        return dict(
            **super(BasicParameterComponent, self).__getstate__(),
            text=self.label,
        )
