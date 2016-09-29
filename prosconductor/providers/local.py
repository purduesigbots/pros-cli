import click
import distutils.dir_util
import fnmatch
import os.path
from proscli.utils import debug, verbose
import prosconfig
from prosconfig.cliconfig import CliConfig
from prosconductor.providers import Identifier, TemplateTypes, TemplateConfig
from prosconductor.providers.utils import get_depots
import shutil
import sys
# from typing import Set, List


def get_local_templates(pros_cfg=None, filters=[],
                        template_types=None):
    if template_types is None or not template_types:
        template_types = [TemplateTypes.kernel, TemplateTypes.library]
    if filters is None or not filters:
        filters = ['.*']
    result = []
    for depot in get_depots(pros_cfg, filters):
        for k, v in depot.list_local(template_types).items():
            result += v
    return result
    # return [Identifier(name=i.name, version=i.version, depot=depot.registrar) for i in [d.values() for d in
    #         [depot.list_local(template_types) for depot in get_depots(pros_cfg, filters)]]]


def create_template(identifier, pros_cli=None):
    if pros_cli is None or not pros_cli:
        pros_cli = CliConfig()
    filename = os.path.join(pros_cli.directory, identifier.depot,
                            '{}-{}'.format(identifier.name, identifier.version),
                            'template.pros')
    config = TemplateConfig(file=filename)
    config.name = identifier.name
    config.version = identifier.version
    config.depot = identifier.depot
    config.save()
    return config


def create_project(identifier, dest, pros_cli=None):
    if pros_cli is None or not pros_cli:
        pros_cli = CliConfig()
    filename = os.path.join(pros_cli.directory, identifier.depot,
                            '{}-{}'.format(identifier.name, identifier.version),
                            'template.pros')
    if not os.path.isfile(filename):
        click.echo('Error: template.pros not found for {}-{}'.format(identifier.name, identifier.version))
        click.get_current_context().abort()
        sys.exit()
    if os.path.isfile(dest) or (os.path.isdir(dest) and len(os.listdir(dest)) > 0):
        click.echo('Error! Destination is a file or a nonempty directory! Delete the file(s) and try again.')
        click.get_current_context().abort()
        sys.exit()
    config = TemplateConfig(file=filename)
    distutils.dir_util.copy_tree(config.directory, dest)
    for root, dirs, files in os.walk(dest):
        for d in dirs:
            if any([fnmatch.fnmatch(d, p) for p in config.template_ignore]):
                verbose('Removing {}'.format(d))
                os.rmdir(os.path.join(root, d))
        for f in files:
            if any([fnmatch.fnmatch(f, p) for p in config.template_ignore]):
                verbose('Removing {}'.format(f))
                os.remove(os.path.join(root, f))
    proj_config = prosconfig.ProjectConfig(dest, create=True)
    proj_config.kernel = identifier.version
    proj_config.save()


def upgrade_project(identifier, dest, pros_cli=None):
    if pros_cli is None or not pros_cli:
        pros_cli = CliConfig()
    filename = os.path.join(pros_cli.directory, identifier.depot,
                            '{}-{}'.format(identifier.name, identifier.version),
                            'template.pros')

    if not os.path.isfile(filename):
        click.echo('Error: template.pros not found for {}-{}'.format(identifier.name, identifier.version))
        click.get_current_context().abort()
        sys.exit()
    proj_config = prosconfig.ProjectConfig(dest, raise_on_error=True)
    config = TemplateConfig(file=filename)

    for root, dirs, files in os.walk(config.directory):
        for d in dirs:
            if any([fnmatch.fnmatch(d, p) for p in config.upgrade_paths]):
                verbose('Upgrading {}'.format(d))
                relpath = os.path.relpath(os.path.join(root, d), config.directory)
                shutil.copytree(os.path.join(config.directory, relpath), os.path.join(proj_config.directory, relpath))
        for f in files:
            if any([fnmatch.fnmatch(f, p) for p in config.upgrade_paths]):
                verbose('Upgrading {}'.format(f))
                relpath = os.path.relpath(os.path.join(root, f), config.directory)
                shutil.copyfile(os.path.join(config.directory, relpath), os.path.join(proj_config.directory, relpath))
