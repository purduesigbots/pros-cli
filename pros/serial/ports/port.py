from typing import *


class Port(object):
    def write(self, data: AnyStr):
        """
        Writes the data to the port
        :param data: a single integer, string, bytes, or a list of integers
        :return: Does not return anything
        """
        pass

    def read(self, n_bytes: int = -1) -> bytes:
        """
        Reads the specified number of bytes
        :param n_bytes: Number of bytes to read.
        If less than 1, then reads all available data as a nonblocking call
        :return: Returns a bytes of length n_bytes (or whatever was available if less than 1)
        """
        pass

    def read_all(self) -> bytes:
        """
        Reads all available bytes
        """
        return self.read(-1)

    def flush(self):
        """
        Flushes the port, if that has any meaning for the port
        """
        pass

    def destroy(self):
        pass
