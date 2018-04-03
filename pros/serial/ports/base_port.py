from typing import *


class BasePort(object):
    def write(self, data: bytes):
        raise NotImplementedError()

    def read(self, n_bytes: int = 0) -> Tuple[bytes, bytes]:
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


class PortException(IOError):
    pass


class PortConnectionException(PortException):
    pass
