import click
import os.path
from proscli.utils import default_cfg, default_options
import prosconductor.providers
from prosconductor.providers import TemplateTypes
import prosconductor.providers.utils
import tabulate
from typing import List


@click.group()
@default_options
def conductor_cli():
    pass


@conductor_cli.group(short_help='Perform project management tasks for PROS')
@default_options
def conduct():
    pass


@conduct.command('lsdepot', short_help='List registered depots')

@default_options
def list_depots():
    depots = prosconductor.providers.utils.get_depot_configs()
    if not bool(depots):
        click.echo('No depots currently registered! Use `pros conduct add-depot` to add a new depot')
    else:
        click.echo([(d.name, d.registrar, d.location) for d in depots])
        click.echo(tabulate.tabulate([(d.name, d.registrar, d.location) for d in depots],
                                     ['Name', 'Registrar', 'Location'], tablefmt='simple'))


def validate_name(ctx, param, value):
    if os.path.isdir(os.path.join(ctx.obj.pros_cfg.directory, value)):
        if value == 'purdueros-mainline':
            raise click.BadParameter('Cannot override purdueros-mainline!')

        click.confirm('A depot with the name {} already exists. Do you want to overwrite it?'.format(value),
                      prompt_suffix=' ', abort=True, default=True)
    return value


def available_providers() -> List[str]:
    return prosconductor.providers.utils.get_all_provider_types().keys()


@conduct.command('add-depot', short_help='Add a depot to PROS')
@click.option('--name', metavar='NAME', prompt=True, callback=validate_name,
              help='Unique name of the new depot')
@click.option('--registrar', metavar='REGISTRAR', prompt=True, type=click.Choice(available_providers()),
              help='Registrar of the new depot')
@click.option('--location', metavar='LOCATION', prompt=True,
              help='Online location of the new depot')
@default_cfg
def add_depot(cfg, name, registrar, location):
    options = prosconductor.providers.utils.get_all_provider_types(cfg.pros_cfg)[registrar](None)\
        .configure_registar_options()
    prosconductor.providers.DepotConfig(name=name, registrar=registrar, location=location, registrar_options=options,
                                        root_dir=cfg.pros_cfg.directory)
    pass


@conduct.command('rm-depot', short_help='Remove a depot from PROS')
@click.option('--name', metavar='NAME', prompt=True, help='Name of the depot')
@default_cfg
def remove_depot(cfg, name):
    if name == 'purdueros-mainline':
        raise click.BadParameter('Cannot delete purdueros-mainline!')

    for depot in [d for d in prosconductor.providers.utils.get_depot_configs(cfg.pros_cfg) if d.name == name]:
        click.echo('Removing {} ({})'.format(depot.name, depot.location))
        depot.delete()


@conduct.command('lstemplate', short_help='List all available templates')
@click.option('--kernels', 'template_types', flag_value=[TemplateTypes.kernel])
@click.option('--libraries', 'template_types', flag_value=[TemplateTypes.library])
@click.option('--all', 'template_types', default=True,
              flag_value=[TemplateTypes.library, TemplateTypes.kernel])
@click.argument('filters', metavar='REGEX', nargs=-1)
@default_cfg
def list_templates(cfg, template_types, filters):
    """
    List templates with the applied filters
    """
    filters = [f for f in filters if f is not None]
    if not filters:
        filters = ['.*']
    if filters != ['.*']:
        click.echo('Providers matching any of {}: {}'
                   .format(filters,
                           [d.name for d in prosconductor.providers.utils.get_depot_configs(cfg.pros_cfg, filters)]))
    result = prosconductor.providers.utils.get_available_templates(cfg.pros_cfg,
                                                                   template_types=template_types,
                                                                   filters=filters)
    if TemplateTypes.kernel in template_types:
        click.echo('Available kernels:')
        click.echo(tabulate.tabulate(
            # complicated list comprehension
            sum([[(i.version, d.depot.config.name, 'online' if d.online else '', 'offline' if d.offline else '') for d in ds]
                 for i, ds in result[TemplateTypes.kernel].items()], []),
            headers=['Version', 'Depot', 'Online', 'Offline']
        ))


@conduct.command(short_help='Download a template')
@click.argument('name', default='kernel')
@click.argument('version', default='latest')
@click.argument('depot', default='auto')
@default_cfg
def download(cfg, name, version, depot):
    """
    Download a template with the specified parameters.

    If the arguments are `download latest` or `download latest kernel`, the latest kernel will be downloaded
    """
    if name == 'latest':
        name = 'kernel'
        if version == 'kernel':
            version = 'latest'

    prosconductor.providers.utils.get_provider(prosconductor.providers.utils.get_depot_config(depot), pros_cfg=cfg.pros_cfg)\
        .download(prosconductor.providers.Identifier(name, version))
