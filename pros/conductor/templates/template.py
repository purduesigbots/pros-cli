from typing import *

from pros.config.config import Config


class Template(Config):
    def __init__(self, file):
        self.name = None  # type: str
        self.version = None  # type: str
        self.supported_kernels = None  # type: str
        self.library_dependencies = {}  # type: set
        self.install_files = []  # type: List[str]
        self.template_ignore = ['template.pros']  # type: List[str]
        self.remove_paths = []  # type: List[str]
        self.upgrade_paths = []  # type: List[str]
        self.origin = None  # type: str
        super(Template, self).__init__(file)
        if 'template.pros' not in self.template_ignore:
            self.template_ignore.append('template.pros')

    @property
    def identifier(self):
        return '{}@{}'.format(self.name, self.version)
