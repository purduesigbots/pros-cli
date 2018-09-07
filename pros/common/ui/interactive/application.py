from typing import *

from .components import Component
from .observable import Observable


class Application(Observable):
    def build(self) -> Generator[Component, None, None]:
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
            app_type=Application.get_hierarchy(self.__class__),
            elements=[e.__getstate__() for e in self.build()]
        )


class Modal(Application):
    def __init__(self, title: AnyStr, description: Optional[AnyStr] = None,
                 will_abort: bool = True, confirm_button: AnyStr = 'Continue', cancel_button: AnyStr = 'Cancel',
                 can_confirm: bool = True):
        super().__init__()
        self.title = title
        self.description = description
        self.will_abort = will_abort
        self.confirm_button = confirm_button
        self.cancel_button = cancel_button
        self._can_confirm = can_confirm

        self.on('confirm', self._confirm)

    def confirm(self, *args, **kwargs):
        pass

    @property
    def can_confirm(self):
        return self._can_confirm

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
