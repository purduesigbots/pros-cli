from typing import *

from semantic_version import Version

from .base_template import BaseTemplate


class Template(BaseTemplate):
    def __init__(self, **kwargs):
        self.system_files: List[str] = []
        self.user_files: List[str] = []
        super().__init__(**kwargs)
        if self.version:
            self.version = str(Version.coerce(self.version))

    @property
    def all_files(self) -> Set[str]:
        return {*self.system_files, *self.user_files}
