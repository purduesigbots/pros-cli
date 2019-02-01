from typing import *

from pros.common.ui.interactive.observable import Observable

T = TypeVar('T')


class Parameter(Observable, Generic[T]):
    """
    A Parameter is an observable value.

    Triggering the "update" event will cause the value to update.
    The Parameter will trigger a "changed" event if the value was updated
    """

    def __init__(self, initial_value: T):
        super().__init__()
        self.value = initial_value

        self.on('update', self.update)

    def update(self, new_value):
        self.value = new_value
        self.trigger('changed', self)

    def on_changed(self, *handlers: Callable, **kwargs):
        return self.on('changed', *handlers, **kwargs)
