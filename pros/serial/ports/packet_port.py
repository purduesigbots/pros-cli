from typing import *

from .port import Port


class PacketPort(Port):
    def subscribe(self, topic: bytes) -> None:
        pass

    def unsubscribe(self, topic: bytes) -> None:
        pass

    def read_packet(self) -> Tuple[bytes, bytes]:
        return bytes(0), bytes(0)
