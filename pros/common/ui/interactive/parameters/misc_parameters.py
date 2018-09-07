from typing import *

from pros.common.ui.interactive.parameters.parameter import Parameter
from pros.common.ui.interactive.parameters.validatable_parameter import ValidatableParameter

T = TypeVar('T')


class OptionParameter(ValidatableParameter, Generic[T]):
    def __init__(self, initial_value: T, options: List[T]):
        super().__init__(initial_value)
        self.options = options

    def validate(self, value: Any):
        return value in self.options


class BooleanParameter(Parameter[bool]):
    pass
