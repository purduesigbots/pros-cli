import typing

from pros.conductor import Project


class SystemDevice(object):
    def upload_project(self, project: Project, **kwargs):
        raise NotImplementedError

    def write_program(self, file: typing.BinaryIO, quirk: int = 0, **kwargs):
        raise NotImplementedError
