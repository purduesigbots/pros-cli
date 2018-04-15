import struct
from typing import *


class JinxSchema(object):
    def __init__(self, n: str, s: str, e: List[str] = None, m: bool = None):
        self.name = n
        self.fmt = s
        self.element_names = e
        self.modifiable = m

    def transform(self, data: bytes) -> Iterable:
        if self.element_names and len(self.element_names) > 0:
            return zip(self.element_names, struct.unpack(self.fmt, data))
        else:
            data = list(struct.unpack(self.fmt, data))
            return data if len(data) > 1 else data[0]
