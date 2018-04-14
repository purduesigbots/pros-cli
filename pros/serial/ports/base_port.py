from typing import *


class BasePort(object):
    def write(self, data: bytes):
        raise NotImplementedError()

    def read(self, n_bytes: int = 0) -> bytes:
        raise NotImplementedError()

    def read_all(self):
        return self.read()

    def config(self, command: str, argument: Any):
        pass

    def flush_input(self):
        pass

    def flush_output(self):
        pass

    def destroy(self):
        pass

    def flush(self):
        self.flush_output()
        self.flush_input()

    @property
    def name(self) -> str:
        raise NotImplementedError


class PortException(IOError):
    pass


class PortConnectionException(PortException):
    pass
