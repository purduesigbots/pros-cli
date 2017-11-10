from pros.config.config import Config
from .template_identifier import TemplateIdentifier


class TemplateConfig(Config):
    def __init__(self, file):
        self.name = None
        self.version = None
        self.__ignored = ['name', 'version']
        self.supported_kernels = None
        self.library_dependencies = {}
        self.template_ignore = []
        self.remove_paths = []
        self.upgrade_paths = []
        super(TemplateConfig, self).__init__(file)

    @property
    def identifier(self):
        return TemplateIdentifier(name=self.name, version=self.version)
