import click
import collections
import os.path


class TemplateIdentifier(collections.namedtuple('Identifier', 'name version')):
    __slots__ = ()

    def __new__(cls, arg):
        if isinstance(arg, LocalTemplateIdentifier):
            (name, version) = (arg.name, arg.version)
        else:
            (name, version) = os.path.basename(arg).split('-')
        return super(TemplateIdentifier, cls).__new__(cls, name, version)

    def __hash__(self):
        return (self.name + self.version).__hash__()

    def iskernel(self):
        return self.name == 'kernel'

    def topath(self, depot):
        return os.path.join(click.get_app_dir('PROS'), depot, '{}-{}'.format(self.name, self.version))


class LocalTemplateIdentifier(collections.namedtuple('Identifier', 'name version depot')):
    __slots__ = ()

    def __new__(cls, path):
        (name, version) = os.path.basename(path).split('-')
        depot = os.path.basename(os.path.dirname(path))
        return super(LocalTemplateIdentifier, cls).__new__(cls, name, version, depot)

    def __new__(cls, template, depot):
        if isinstance(template, TemplateIdentifier):
            (name, version) = (template.name, template.version)
        else:
            (name, version) = template
        return super(LocalTemplateIdentifier, cls).__new__(cls, name, version, depot)

    def __hash__(self):
        return (self.name + self.version + self.depot).__hash__()