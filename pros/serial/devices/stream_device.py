from typing import *

from .generic_device import GenericDevice


class StreamDevice(GenericDevice):
    def subscribe(self, topic: bytes):
        raise NotImplementedError

    def unsubscribe(self, topic: bytes):
        raise NotImplementedError

    @property
    def promiscuous(self):
        raise NotImplementedError

    @promiscuous.setter
    def promiscuous(self, value: bool):
        raise NotImplementedError

    def read(self) -> Tuple[bytes, bytes]:
        raise NotImplementedError

    def write(self, data: Union[bytes, str]):
        raise NotImplementedError


class RawStreamDevice(StreamDevice):

    def subscribe(self, topic: bytes):
        pass

    def unsubscribe(self, topic: bytes):
        pass

    @property
    def promiscuous(self):
        return False

    @promiscuous.setter
    def promiscuous(self, value: bool):
        pass

    def read(self) -> Tuple[bytes, bytes]:
        return b'', self.port.read_all()

    def write(self, data: Union[bytes, str]):
        self.port.write(data)
