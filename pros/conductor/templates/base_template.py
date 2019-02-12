from typing import *

from semantic_version import Spec, Version

from pros.common import ui


class BaseTemplate(object):
    def __init__(self, **kwargs):
        self.name: str = None
        self.version: str = None
        self.supported_kernels: str = None
        self.target: str = None
        self.metadata: Dict[str, Any] = {}
        if 'orig' in kwargs:
            self.__dict__.update({k: v for k, v in kwargs.pop('orig').__dict__.items() if k in self.__dict__})
        self.__dict__.update({k: v for k, v in kwargs.items() if k in self.__dict__})
        self.metadata.update({k: v for k, v in kwargs.items() if k not in self.__dict__})
        if 'depot' in self.metadata and 'origin' not in self.metadata:
            self.metadata['origin'] = self.metadata.pop('depot')
        if 'd' in self.metadata and 'depot' not in self.metadata:
            self.metadata['depot'] = self.metadata.pop('d')
        if 'l' in self.metadata and 'location' not in self.metadata:
            self.metadata['location'] = self.metadata.pop('l')
        if self.name == 'pros':
            self.name = 'kernel'

    def satisfies(self, query: 'BaseTemplate', kernel_version: Union[str, Version] = None) -> bool:
        if query.name and self.name != query.name:
            return False
        if query.target and self.target != query.target:
            return False
        if query.version and Version(self.version) not in Spec(query.version):
            return False
        if kernel_version and isinstance(kernel_version, str):
            kernel_version = Version(kernel_version)
        if self.supported_kernels and kernel_version and kernel_version not in Spec(self.supported_kernels):
            return False
        keys_intersection = set(self.metadata.keys()).intersection(query.metadata.keys())
        # Find the intersection of the keys in the template's metadata with the keys in the query metadata
        # This is what allows us to throw all arguments into the query metadata (from the CLI, e.g. those intended
        # for the depot or template application hints)
        if any([self.metadata[k] != query.metadata[k] for k in keys_intersection]):
            return False
        return True

    def __str__(self):
        fields = [self.metadata.get("origin", None), self.target, self.__class__.__name__]
        additional = ", ".join(map(str, filter(bool, fields)))
        return f'{self.identifier} ({additional})'

    def __gt__(self, other):
        if isinstance(other, BaseTemplate):
            # TODO: metadata comparison
            return self.name == other.name and Version(self.version) > Version(other.version)
        else:
            return False

    def __eq__(self, other):
        if isinstance(other, BaseTemplate):
            return self.identifier == other.identifier
        else:
            return super().__eq__(other)

    def __hash__(self):
        return self.identifier.__hash__()

    def as_query(self, version='>0', metadata=False, **kwargs):
        if isinstance(metadata, bool) and not metadata:
            metadata = dict()
        return BaseTemplate(orig=self, version=version, metadata=metadata, **kwargs)

    @property
    def identifier(self):
        return f'{self.name}@{self.version}'

    @property
    def origin(self):
        return self.metadata.get('origin', 'Unknown')

    @classmethod
    def create_query(cls, name: str = None, **kwargs) -> 'BaseTemplate':
        if not isinstance(name, str):
            return cls(**kwargs)
        if name.count('@') > 1:
            raise ValueError(f'Malformed identifier: {name}')
        if '@' in name:
            name, kwargs['version'] = name.split('@')
        if kwargs.get('version', 'latest') == 'latest':
            kwargs['version'] = '>=0'
        if name == 'kernal':
            ui.echo("Assuming 'kernal' is the British spelling of kernel.")
            name = 'kernel'
        return cls(name=name, **kwargs)
