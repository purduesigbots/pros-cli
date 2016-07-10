import click
import collections
import enum
import os.path
from prosconfig import Config
from typing import List, Dict, Set


class InvalidIdentifierException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super(InvalidIdentifierException, self).__init__(args, kwargs)


Identifier = collections.namedtuple('Identifier', ['name', 'version'])


class TemplateTypes(enum.Enum):
    kernel = 1 << 0
    library = 1 << 1


TemplateDescriptor = collections.namedtuple('TemplateDescriptor', ['depot', 'offline', 'online'])


class DepotConfig(Config):
    def __init__(self,
                 file: str=None,
                 name: str=None, registrar: str=None, location: str=None,
                 registrar_options: dict=None,
                 types: List[TemplateTypes]=None,
                 root_dir: str=None):
        self.name = name  # type: str
        self.registrar = registrar  # type: str
        self.location = location  # type: str
        self.types = types if types is not None else []  # type: List[TemplateTypes]
        self.registrar_options = registrar_options if registrar_options is not None else dict()  # type: Dict[str, str]
        if not file:
            file = os.path.join((root_dir if root_dir is not None else click.get_app_dir('PROS')), name, 'depot.pros')
        super(DepotConfig, self).__init__(file)

    def delete(self):
        super(DepotConfig, self).delete()
        os.removedirs(self.directory)


class TemplateConfig(Config):
    def __init__(self, file):
        self.name = None  # type: str
        self.version = None  # type: str
        self.depot = None  # type: DepotConfig
        self.template_ignore = []  # type: List[str]
        self.upgrade_paths = []  # type: List[str]
        super(TemplateConfig, self).__init__(file)


class DepotProvider(object):
    registrar = 'default-provider'

    def __init__(self, config: DepotConfig):
        self.config = config

    def list_all(self, template_types: List[TemplateTypes]=None) -> Dict[TemplateTypes, List[Identifier]]:
        pass

    def list_latest(self, name: str):
        """

        :param name:
        :return:
        """
        pass

    def download(self, identifier: Identifier):
        """
        Downloads the specified template with the given name and version
        :return:
        """
        pass

    def list_local(self, template_types: List[TemplateTypes]=None) -> Dict[TemplateTypes, Set[Identifier]]:
        if template_types is None:
            template_types = [TemplateTypes.kernel, TemplateTypes.library]

        result = dict()  # type: Dict[TemplateTypes, Set[Identifier]]
        for template_type in template_types:
            result[template_type] = set()

        for item in [os.path.join(self.config.directory, x) for x in os.listdir(self.config.directory)
                                   if os.path.isdir(os.path.join(self.config.directory, x))]:
            if TemplateTypes.kernel in template_types and 'kernel.pros' in os.listdir(item):
                template_config = TemplateConfig(os.path.join(item, 'kernel.pros'))
                result[TemplateTypes.kernel].add(Identifier(name=template_config.name,
                                                               version=template_config.version))
        return result

    @staticmethod
    def configure_registar_options():
        pass

