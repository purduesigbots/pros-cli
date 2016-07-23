import click
import collections
import enum
import os.path
from prosconfig import Config
import shutil
from typing import List, Dict, Set, Union


class InvalidIdentifierException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super(InvalidIdentifierException, self).__init__(args, kwargs)


class Identifier(collections.namedtuple('Identifier', ['name', 'version', 'depot'])):
    def __hash__(self):
        return (self.name + self.version + self.depot).__hash__()

# Identifier = collections.namedtuple('Identifier', ['name', 'version', 'depot_registrar'])


class TemplateTypes(enum.Enum):
    kernel = 1 << 0
    library = 1 << 1


TemplateDescriptor = collections.namedtuple('TemplateDescriptor', ['depot', 'offline', 'online'])


class DepotConfig(Config):
    def __init__(self,
                 file: str = None,
                 name: str = None, registrar: str = None, location: str = None,
                 registrar_options: dict = None,
                 types: List[TemplateTypes] = None,
                 root_dir: str = None):
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
        shutil.rmtree(self.directory)


class TemplateConfig(Config):
    def __init__(self, file):
        self.name = None  # type: str
        self.version = None  # type: str
        self.depot = None  # type: str
        self.template_ignore = []  # type: List[str]
        self.upgrade_paths = []  # type: List[str]
        super(TemplateConfig, self).__init__(file)

    @property
    def identifier(self):
        return Identifier(name=self.name, version=self.version, depot=self.depot)


class DepotProvider(object):
    registrar = 'default-provider'

    def __init__(self, config: DepotConfig):
        self.config = config

    def list_online(self, template_types: List[TemplateTypes] = None) -> Dict[TemplateTypes, Set[Identifier]]:
        pass

    def list_latest(self, name: str):
        """

        :param name:
        :return:
        """
        pass

    def download(self, identifier: Identifier) -> bool:
        """
        Downloads the specified template with the given name and version
        :return: True if successful, False if not
        """
        pass

    def list_local(self, template_types: List[TemplateTypes] = None) -> Dict[TemplateTypes, Set[Identifier]]:
        if template_types is None:
            template_types = [TemplateTypes.kernel, TemplateTypes.library]

        result = dict()  # type: Dict[TemplateTypes, Set[Identifier]]
        for template_type in template_types:
            result[template_type] = set()

        for item in [os.path.join(self.config.directory, x) for x in os.listdir(self.config.directory)
                     if os.path.isdir(os.path.join(self.config.directory, x))]:
            if TemplateTypes.kernel in template_types and 'template.pros' in os.listdir(item):
                template_config = TemplateConfig(os.path.join(item, 'template.pros'))
                result[TemplateTypes.kernel].add(template_config.identifier)
        return result

    def verify_configuration(self) -> bool:
        """
        Verifies the current configuration (i.e. is the location valid)
        :return: Something falsey if valid, an exception (to be raised or displayed)
        """
        pass

    @staticmethod
    def configure_registrar_options(default: dict=dict()) -> dict:
        pass


def get_template_dir(depot: Union[str, DepotConfig, DepotProvider], identifier: Identifier) -> str:
    if isinstance(depot, DepotConfig):
        depot = depot.name
    elif isinstance(depot, DepotProvider):
        depot = depot.config.name
    elif not isinstance(depot, str):
        raise ValueError('Depot must a str, DepotConfig, or DepotProvider')
    assert isinstance(depot, str)
    return os.path.join(click.get_app_dir('PROS'), depot, '{}-{}'.format(identifier.name, identifier.version))
