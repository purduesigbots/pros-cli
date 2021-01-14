from typing import *

from cobs import cobs
from pros.common.utils import logger
from pros.serial.devices.stream_device import StreamDevice
from pros.serial.ports import BasePort


class V5UserDevice(StreamDevice):
    def __init__(self, port: BasePort):
        super().__init__(port)
        self.topics: Set[bytes] = set()
        self._accept_all = False
        self.buffer: bytearray = bytearray()

    def subscribe(self, topic: bytes):
        self.topics.add(topic)

    def unsubscribe(self, topic: bytes):
        self.topics.remove(topic)

    @property
    def promiscuous(self):
        return self._accept_all

    @promiscuous.setter
    def promiscuous(self, value: bool):
        self._accept_all = True

    def write(self, data: Union[str, bytes]):
        if isinstance(data, str):
            data = data.encode(encoding='ascii')
        self.port.write(data)

    def read(self) -> Tuple[bytes, bytes]:
        msg = None, None
        while msg[0] is None or (msg[0] not in self.topics and not self._accept_all):
            while b'\0' not in self.buffer:
                self.buffer.extend(self.port.read(1))
                self.buffer.extend(self.port.read(-1))
            assert b'\0' in self.buffer
            msg, self.buffer = self.buffer.split(b'\0', 1)
            try:
                msg = cobs.decode(msg)
            except cobs.DecodeError:
                logger(__name__).warning(f'Could not decode bytes: {msg.hex()}')
            assert len(msg) >= 4
            msg = bytes(msg[:4]), bytes(msg[4:])
        return msg
