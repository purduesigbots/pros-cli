import sys
from typing import *

from .components import Component
from .observable import Observable
from .parameters import ValidatableParameter


class Application(Observable):
    """
    An Application manages the lifecycle of an interactive UI that is rendered to the users. It creates a view for the
    model the application is rendering.
    """
    def build(self) -> Generator[Component, None, None]:
        """
        Creates a list of components to render
        """
        raise NotImplementedError()

    def on_exit(self, *handlers: Callable):
        return super(Application, self).on('end', *handlers)

    def exit(self):
        self.trigger('end')

    def on_redraw(self, *handlers: Callable, **kwargs):
        return super(Application, self).on('redraw', *handlers, **kwargs)

    def redraw(self):
        self.trigger('redraw')

    @staticmethod
    def on_updated(event, handler):
        def binding(self):
            return self.on(event, handler)

        return binding

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

    def __getstate__(self):
        return dict(
            etype=Application.get_hierarchy(self.__class__),
            elements=[e.__getstate__() for e in self.build()],
            uuid=self.uuid
        )


class Modal(Application):
    """
    An Application which is typically displayed in a pop-up box. It has a title, description, continue button,
    and cancel button.
    """
    def __init__(self, title: AnyStr, description: Optional[AnyStr] = None,
                 will_abort: bool = True, confirm_button: AnyStr = 'Continue', cancel_button: AnyStr = 'Cancel',
                 can_confirm: Optional[bool] = None):
        super().__init__()
        self.title = title
        self.description = description
        self.will_abort = will_abort
        self.confirm_button = confirm_button
        self.cancel_button = cancel_button
        self._can_confirm = can_confirm

        self.on('confirm', self._confirm)

    def confirm(self, *args, **kwargs):
        raise NotImplementedError()

    @property
    def can_confirm(self):
        if self._can_confirm is not None:
            return self._can_confirm
        return all([
            p.is_valid
            for p in vars(self)
            if isinstance(p, ValidatableParameter)
        ])

    def build(self) -> Generator[Component, None, None]:
        raise NotImplementedError()

    def __getstate__(self):
        extra_state = {}
        if self.description is not None:
            extra_state['description'] = self.description
        return dict(
            **super(Modal, self).__getstate__(),
            **extra_state,
            title=self.title,
            will_abort=self.will_abort,
            confirm_button=self.confirm_button,
            cancel_button=self.cancel_button,
            can_confirm=self.can_confirm
        )

    def _confirm(self, *args, **kwargs):
        if self.can_confirm:
            self.confirm(*args, **kwargs)
        else:
            self.redraw()
