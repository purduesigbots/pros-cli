from typing import *

from semantic_version import Version

from .base_template import BaseTemplate


class Template(BaseTemplate):
    def __init__(self, **kwargs):
        self.system_files: List[str] = []
        self.user_files: List[str] = []
        if 'version' in kwargs:
            kwargs['version'] = str(Version.coerce(kwargs['version']))
        super().__init__(**kwargs)

    @property
    def all_files(self) -> Set[str]:
        return {*self.system_files, *self.user_files}
