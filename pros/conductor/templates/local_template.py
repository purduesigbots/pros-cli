import os

from .template import Template


def _fix_path(*paths: str) -> str:
    return os.path.normpath(os.path.join(*paths).replace('\\', '/'))


class LocalTemplate(Template):
    def __init__(self, **kwargs):
        self.location: str = None
        super().__init__(**kwargs)

    @property
    def real_user_files(self):
        return filter(lambda f: os.path.exists(_fix_path(self.location, f)), self.user_files)

    @property
    def real_system_files(self):
        return filter(lambda f: os.path.exists(_fix_path(self.location, f)), self.system_files)

    def __hash__(self):
        return self.identifier.__hash__()
