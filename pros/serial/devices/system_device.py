import typing


class SystemDevice(object):
    def write_program(self, file: typing.BinaryIO, quirk: int = 0, **kwargs):
        raise NotImplementedError
