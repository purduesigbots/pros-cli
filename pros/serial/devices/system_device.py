import typing


class SystemDevice(object):
    def write_program(self, file: typing.BinaryIO, **kwargs):
        raise NotImplementedError
