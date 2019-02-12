from functools import wraps
from typing import *
from uuid import uuid4 as uuid

import observable

from pros.common import logger

_uuid_table = dict()  # type: Dict[str, Observable]


class Observable(observable.Observable):
    """
    Wrapper class for the observable package for use in interactive UI. It registers itself with a global registry
    to facilitate updates from any context (e.g. from a renderer).
    """

    @classmethod
    def notify(cls, uuid, event, *args, **kwargs):
        """
        Triggers an Observable given its UUID. See arguments for Observable.trigger
        """
        if isinstance(uuid, Observable):
            uuid = uuid.uuid
        if uuid in _uuid_table:
            _uuid_table[uuid].trigger(event, *args, **kwargs)
        else:
            logger(__name__).warning(f'Could not find an Observable to notify with UUID: {uuid}', sentry=True)

    def on(self, event, *handlers,
           bound_args: Tuple[Any, ...] = None, bound_kwargs: Dict[str, Any] = None,
           asynchronous: bool = False) -> Callable:
        """
        Sets up a callable to be called whenenver "event" is triggered
        :param event: Event to bind to. Most classes expose an e.g. "on_changed" wrapper which provides the correct
                      event string
        :param handlers: A list of Callables to call when event is fired
        :param bound_args:  Bind ordered arguments to the Callable. These are supplied before the event's supplied
                            arguments
        :param bound_kwargs: Bind keyword arguments to the Callable. These are supplied before the event's supplied
                            kwargs. They should not conflict with the supplied event kwargs
        :param asynchronous: If true, the Callable will be called in a new thread. Useful if the work to be done from
                             an event takes a long time to process
        :return:
        """
        if bound_args is None:
            bound_args = []
        if bound_kwargs is None:
            bound_kwargs = {}

        if asynchronous:
            def bind(h):
                def bound(*args, **kw):
                    from threading import Thread
                    from pros.common.utils import with_click_context
                    t = Thread(target=with_click_context(h), args=(*bound_args, *args), kwargs={**bound_kwargs, **kw})
                    t.start()
                    return t

                return bound
        else:
            def bind(h):
                @wraps(h)
                def bound(*args, **kw):
                    return h(*bound_args, *args, **bound_kwargs, **kw)

                return bound

        return super(Observable, self).on(event, *[bind(h) for h in handlers])

    def trigger(self, event, *args, **kw):
        logger(__name__).debug(f'Triggered {self.uuid} ({type(self).__name__}) "{event}" event: {args} {kw}')
        return super().trigger(event, *args, **kw)

    def __init__(self):
        self.uuid = str(uuid())
        _uuid_table[self.uuid] = self
        super(Observable, self).__init__()
