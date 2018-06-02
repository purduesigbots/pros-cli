from typing import *

from pros.serial import bytes_to_str


class Message(bytes):
    def __new__(cls, rx: bytes, tx: bytes, internal_rx: Union[bytes, int] = None,
                bookmarks: Dict[str, bytes] = None):
        if internal_rx is None:
            internal_rx = rx
        if isinstance(internal_rx, int):
            internal_rx = bytes([internal_rx])
        return super().__new__(cls, internal_rx)

    def __init__(self, rx: bytes, tx: bytes, internal_rx: Union[bytes, int] = None,
                 bookmarks: Dict[str, bytes] = None):
        if internal_rx is None:
            internal_rx = rx
        if isinstance(internal_rx, int):
            internal_rx = bytes([internal_rx])
        self.rx = rx
        self.tx = tx
        self.internal_rx = internal_rx
        self.bookmarks = {} if bookmarks is None else bookmarks
        super().__init__()

    def __getitem__(self, item):
        if isinstance(item, str) and item in self.bookmarks.keys():
            return self.bookmarks[item]
        if isinstance(item, int):
            return super().__getitem__(item)
        return type(self)(self.rx, self.tx, internal_rx=self.internal_rx[item], bookmarks=self.bookmarks)

    def __setitem__(self, key, value):
        self.bookmarks[key] = value

    def __str__(self):
        return 'TX:{}\tRX:{}'.format(bytes_to_str(self.tx), bytes_to_str(self.rx))
