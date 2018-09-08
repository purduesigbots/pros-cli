from typing import *

from pros.common.ui.interactive.parameters.parameter import Parameter

T = TypeVar('T')


class ValidatableParameter(Parameter, Generic[T]):
    """
    A ValidatableParameter is a parameter which has some restriction on valid values.
    """
    def __init__(self, initial_value: T, allow_invalid_input: bool = True):
        """
        :param allow_invalid_input: Allow invalid input to be propagated to the `changed` event
        """
        super().__init__(initial_value)
        self.allow_invalid_input = allow_invalid_input

    def validate(self, value: T) -> bool:
        raise NotImplementedError()

    def is_valid(self, value: T = None) -> bool:
        return self.validate(value if value is not None else self.value)

    def update(self, new_value):
        if self.allow_invalid_input or self.is_valid(new_value):
            super(ValidatableParameter, self).update(new_value)
            if self.is_valid():
                self.trigger('changed_validated', self)

    def on_changed(self, *handlers: Callable, **kwargs):
        """
        Subscribe to event whenever value validly changes
        """
        return self.on('changed_validated', *handlers, **kwargs)

    def on_any_changed(self, *handlers: Callable, **kwargs):
        """
        Subscribe to event whenever value changes (regardless of whether or not new value is valid)
        """
        return self.on('changed', *handlers, **kwargs)
