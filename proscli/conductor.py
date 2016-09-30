import click
from collections import OrderedDict
import json
import os.path
import proscli.utils
from proscli.utils import default_cfg, default_options, AliasGroup
import prosconductor.providers as providers
from prosconductor.providers import TemplateTypes, Identifier
import prosconductor.providers.local as local
import prosconductor.providers.utils as utils
import prosconfig
import semantic_version as semver
import sys
import tabulate
# from typing import List


def first_run(ctx: proscli.utils.State, force=False, defaults=False):
    if len(utils.get_depot_configs(ctx.pros_cfg)) == 0:
        click.echo('You don\'t currently have any depots configured.')
    if len(utils.get_depot_configs(ctx.pros_cfg)) == 0 or force:
        if defaults or click.confirm('Add the official PROS kernel depot, pros-mainline?', default=True):
            click.get_current_context().invoke(add_depot, name='pros-mainline',
                                               registrar='github-releases',
                                               location='purduesigbots/pros',
                                               configure=False)
            click.echo('Added pros-mainline to available depots. '
                       'Add more depots in the future by running `pros conduct add-depot`\n')
            if defaults or click.confirm('Download the latest kernel?', default=True):
                click.get_current_context().invoke(download, name='kernel', depot='pros-mainline')


@click.group(cls=AliasGroup)
@default_options
def conductor_cli():
    pass


@conductor_cli.group(cls=AliasGroup, short_help='Perform project management tasks for PROS', aliases=['cond', 'c'])
@default_options
def conduct():
    pass


# region Depot Management
@conduct.command('lsdepot', short_help='List registered depots',
                 aliases=['lsd', 'list-depots', 'lsdpt', 'depots'])
@default_cfg
def list_depots(cfg):
    first_run(cfg)
    depots = utils.get_depot_configs()
    if not bool(depots):
        click.echo('No depots currently registered! Use `pros conduct add-depot` to add a new depot')
    else:
        click.echo([(d.name, d.registrar, d.location) for d in depots])
        click.echo(tabulate.tabulate([(d.name, d.registrar, d.location) for d in depots],
                                     ['Name', 'Registrar', 'Location'], tablefmt='simple'))


def validate_name(ctx, param, value):
    if os.path.isdir(os.path.join(ctx.obj.pros_cfg.directory, value)):
        if value == 'pros-mainline':
            raise click.BadParameter('Cannot override pros-mainline!')

        click.confirm('A depot with the name {} already exists. Do you want to overwrite it?'.format(value),
                      prompt_suffix=' ', abort=True, default=True)
    return value


def available_providers():
    return utils.get_all_provider_types().keys()


@conduct.command('add-depot', short_help='Add a depot to PROS', aliases=['new-depot', 'add-provider', 'new-provider'])
@click.option('--name', metavar='NAME', prompt=True, callback=validate_name,
              help='Unique name of the new depot')
@click.option('--registrar', metavar='REGISTRAR', prompt=True, type=click.Choice(available_providers()),
              help='Registrar of the new depot')
@click.option('--location', metavar='LOCATION', prompt=True,
              help='Online location of the new depot')
@click.option('--configure/--no-configure', default=True)
@default_cfg
def add_depot(cfg, name, registrar, location, configure):
    if configure:
        options = utils.get_all_provider_types(cfg.pros_cfg)[registrar](None) \
            .configure_registrar_options()
    else:
        options = dict()
    providers.DepotConfig(name=name, registrar=registrar, location=location, registrar_options=options,
                          root_dir=cfg.pros_cfg.directory)
    pass


@conduct.command('rm-depot', short_help='Remove a depot from PROS')
@click.option('--name', metavar='NAME', prompt=True, help='Name of the depot')
@default_cfg
def remove_depot(cfg, name):
    if name == 'pros-mainline':
        raise click.BadParameter('Cannot delete pros-mainline!')

    for depot in [d for d in utils.get_depot_configs(cfg.pros_cfg) if d.name == name]:
        click.echo('Removing {} ({})'.format(depot.name, depot.location))
        depot.delete()


@conduct.command('config-depot', short_help='Configure a depot')
@click.option('--name', metavar='NAME', prompt=True, help='Name of the depot')
@default_cfg
def config_depot(cfg, name):
    if name not in [d.name for d in utils.get_depot_configs(cfg.pros_cfg)]:
        click.echo('{} isn\'t a registered depot! Have you added it using `pros conduct add-depot`?')
        click.get_current_context().abort()
        sys.exit()
    depot = [d for d in utils.get_depot_configs(cfg.pros_cfg) if d.name == name][0]
    depot.registrar_options = utils.get_all_provider_types(cfg.pros_cfg)[depot.registrar](None) \
        .configure_registrar_options(default=depot.registrar_options)
    depot.save()


# endregion


# region Template Management
@conduct.command('lstemplate', short_help='List all available templates',
                 aliases=['lst', 'templates', 'list-templates', 'lstmpl', 'lstemplates'])
@click.option('--kernels', 'template_types', flag_value=[TemplateTypes.kernel])
@click.option('--libraries', 'template_types', flag_value=[TemplateTypes.library])
@click.option('--all', 'template_types', default=True,
              flag_value=[TemplateTypes.library, TemplateTypes.kernel])
@click.option('--offline-only', is_flag=True, default=False, help='List only only templates available locally')
@click.argument('filters', metavar='REGEX', nargs=-1)
@default_cfg
def list_templates(cfg, template_types, filters, offline_only):
    """
    List templates with the applied filters
    """
    first_run(cfg)
    filters = [f for f in filters if f is not None]
    if not filters:
        filters = ['.*']
    if filters != ['.*']:
        click.echo('Providers matching any of {}: {}'
                   .format(filters,
                           [d.name for d in utils.get_depot_configs(cfg.pros_cfg, filters)]))
    result = utils.get_available_templates(cfg.pros_cfg,
                                           template_types=template_types,
                                           filters=filters,
                                           offline_only=offline_only)
    table = sum(
        [[(i.version, d.depot.config.name, 'online' if d.online else '', 'offline' if d.offline else '') for d in ds]
         for i, ds in result[TemplateTypes.kernel].items()], [])
    if TemplateTypes.kernel in template_types:
        if not cfg.machine_output:
            click.echo('Available kernels:')
            click.echo(tabulate.tabulate(table, headers=['Version', 'Depot', 'Online', 'Offline']))
        else:
            table = [{
                         'version': e[0],
                         'depot': e[1],
                         'online': e[2] == 'online',
                         'offline': e[3] == 'offline'
                     }
                     for e in table]
            click.echo(json.dumps(table))


@conduct.command(short_help='Download a template', aliases=['dl'])
@click.argument('name', default='kernel')
@click.argument('version', default='latest')
@click.argument('depot', default='auto')
@click.option('--no-check', '-nc', is_flag=True, default=False,
              help='If all arguments are given, then checks if the template exists won\'t be performed '
                   'before attempting to download.')
@default_cfg
def download(cfg, name, version, depot, no_check):
    """
    Download a template with the specified parameters.

    If the arguments are `download latest` or `download latest kernel`, the latest kernel will be downloaded
    """
    first_run(cfg)
    if name.lower() == 'kernel':
        name = 'kernel'
    elif name == 'latest':
        name = 'kernel'
        if version == 'kernel':
            version = 'latest'

    if version == 'latest' or depot == 'auto' or not no_check:
        click.echo('Fetching online listing to verify available templates.')
        listing = utils.get_available_templates(pros_cfg=cfg.pros_cfg,
                                                template_types=[utils.TemplateTypes.kernel if name == 'kernel'
                                                                else utils.TemplateTypes.library])
        listing = listing.get(utils.TemplateTypes.kernel if name == 'kernel' else utils.TemplateTypes.library)
        listing = {i: d for (i, d) in listing.items() if i.name == name}
        if len(listing) == 0:
            click.echo('No templates were found with the name {}'.format(name))
            click.get_current_context().abort()
            sys.exit()

        if not depot == 'auto':
            if depot not in [d.depot.config.name for ds in listing.values() for d in ds]:
                click.echo('No templates for {} were found on {}'.format(name, depot))
                click.get_current_context().abort()
                sys.exit()
            listing = {i: [d for d in ds if d.depot.config.name == depot] for i, ds in listing.items()
                       if depot in [d.depot.config.name for d in ds]}

        # listing now filtered for depots, if applicable

        if version == 'latest':
            identifier, descriptors = OrderedDict(sorted(listing.items(), key=lambda kvp: semver.Version(kvp[0].version))).popitem()
            click.echo('Resolved {} {} to {} {}'.format(name, version, identifier.name, identifier.version))
        else:
            if version not in [i.version for (i, d) in listing.items()]:
                click.echo('No templates for {} were found with the version {}'.format(name, version))
                click.get_current_context().abort()
                sys.exit()
            identifier, descriptors = [(i, d) for (i, d) in listing.items() if i.version == version][0]

        # identifier is now selected...
        if len(descriptors) == 0:
            click.echo('No templates for {} were found with the version {}'.format(name, version))
            click.get_current_context().abort()
            sys.exit()

        if len(descriptors) > 1:
            if name == 'kernel' and depot == 'auto' and 'pros-mainline' in [desc.depot.config.name for desc in
                                                                                 descriptors]:
                descriptor = [desc for desc in descriptors if desc.depot.config.name == 'pros-mainline']
            else:
                click.echo('Multiple depots for {}-{} were found. Please specify a depot: '.
                           format(identifier.name, identifier.version))
                options_table = sorted([(descriptors.index(desc), desc.depot.config.name) for desc in descriptors],
                                       key=lambda l: l[1])
                click.echo(tabulate.tabulate(options_table, headers=['', 'Depot']))
                result = click.prompt('Which depot?', default=options_table[0][1],
                                      type=click.Choice(
                                          [str(i) for (i, n) in options_table] + [n for (i, n) in options_table]))
                if result in [str(i) for (i, n) in options_table]:
                    descriptor = [d for d in descriptors if d.depot.config.name == options_table[int(result)][1]][0]
                else:
                    descriptor = [d for d in descriptors if d.depot.config.name == result][0]
        elif depot == 'auto' or descriptors[0].depot.config.name == depot:
            descriptor = descriptors[0]
        else:
            click.echo('Could not find a depot to download {} {}'.format(name, version))
            click.get_current_context().abort()
            sys.exit()
    else:
        identifier = providers.Identifier(name=name, version=version)
        descriptor = utils.TemplateDescriptor(depot=utils.get_depot(utils.get_depot_config(name=depot,
                                                                                           pros_cfg=cfg.pros_cfg)),
                                              offline=False,
                                              online=True)

    click.echo('Downloading {} {} from {} using {}'.format(identifier.name,
                                                           identifier.version,
                                                           descriptor.depot.config.name,
                                                           descriptor.depot.registrar))
    descriptor.depot.download(identifier)
    if identifier.name == 'kernel':
        click.echo('''To create a new PROS project with this kernel, run `pros conduct new <folder> {0} {1}`,
or to upgrade an existing project, run `pros conduct upgrade <folder> {0} {1}'''
                   .format(identifier.version, identifier.depot))
        # todo: add helpful text for how to create a project or add the new library to a project


@conduct.command('create-template', short_help='Creates a template with the specified name, version, and depot')
@click.argument('name')
@click.argument('version')
@click.argument('depot')
@default_cfg
def create_template(cfg, name, version, depot):
    first_run(cfg)
    template = local.create_template(utils.Identifier(name, version, depot))
    click.echo('Created template at {}'.format(template.save_file))


# endregion


# region Project Management
@conduct.command('new', aliases=['new-proj', 'new-project', 'create', 'create-proj', 'create-project'],
                 short_help='Creates a new PROS project')
@click.argument('location')
@click.argument('kernel', default='latest')
@click.argument('depot', default='auto')
@click.option('--verify-only', is_flag=True, default=False)
@default_cfg
def new(cfg, kernel, location, depot, verify_only):
    first_run(cfg)
    templates = local.get_local_templates(pros_cfg=cfg.pros_cfg,
                                          template_types=[TemplateTypes.kernel])  # type: Set[Identifier]
    if not templates or len(templates) == 0:
        click.echo('No templates have been downloaded! Use `pros conduct download` to download the latest kernel.')
        click.get_current_context().abort()
        sys.exit()
    kernel_version = kernel
    if kernel == 'latest':
        kernel_version = sorted(templates, key=lambda t: semver.Version(t.version))[-1].version
        proscli.utils.debug('Resolved version {} to {}'.format(kernel, kernel_version))
    templates = [t for t in templates if t.version == kernel_version]  # type: List[Identifier]
    depot_registrar = depot
    if depot == 'auto':
        templates = [t for t in templates if t.version == kernel_version]
        if not templates or len(templates) == 0:
            click.echo('No templates exist for {}'.format(kernel_version))
            click.get_current_context().abort()
            sys.exit()
        if 'pros-mainline' in [t.depot for t in templates]:
            depot_registrar = 'pros-mainline'
        else:
            depot_registrar = [t.depot for t in templates][0]
        proscli.utils.debug('Resolved depot {} to {}'.format(depot, depot_registrar))
    templates = [t for t in templates if t.depot == depot_registrar]
    if not templates or len(templates) == 0:
        click.echo('No templates were found for kernel version {} on {}'.format(kernel_version, depot_registrar))
        click.get_current_context().abort()
        sys.exit()
    template = templates[0]
    if not os.path.isabs(location):
        location = os.path.abspath(location)
    click.echo('Creating new project from {} on {} at {}'.format(template.version, template.depot, location))
    local.create_project(identifier=template, dest=location, pros_cli=cfg.pros_cfg)


@conduct.command('upgrade', aliases=['update'], help='Upgrades a PROS project')
@click.argument('location')
@click.argument('kernel', default='latest')
@click.argument('depot', default='auto')
@default_cfg
def upgrade(cfg, kernel, location, depot):
    first_run(cfg)
    templates = local.get_local_templates(pros_cfg=cfg.pros_cfg,
                                          template_types=[TemplateTypes.kernel])  # type: List[Identifier]
    if not templates or len(templates) == 0:
        click.echo('No templates have been downloaded! Use `pros conduct download` to download the latest kernel.')
        click.get_current_context().abort()
        sys.exit()
    kernel_version = kernel
    if kernel == 'latest':
        kernel_version = sorted(templates, key=lambda t: semver.Version(t.version))[-1].version
        proscli.utils.debug('Resolved version {} to {}'.format(kernel, kernel_version))
    templates = [t for t in templates if t.version == kernel_version]
    depot_registrar = depot
    if depot == 'auto':
        templates = [t for t in templates if t.version == kernel_version]
        if not templates or len(templates) == 0:
            click.echo('No templates exist for {}'.format(kernel_version))
            click.get_current_context().abort()
            sys.exit()
        if 'pros-mainline' in [t.depot for t in templates]:
            depot_registrar = 'pros-mainline'
        else:
            depot_registrar = [t.depot for t in templates][0]
        proscli.utils.debug('Resolved depot {} to {}'.format(depot, depot_registrar))
    templates = [t for t in templates if t.depot == depot_registrar]
    if not templates or len(templates) == 0:
        click.echo('No templates were found for kernel version {} on {}'.format(kernel_version, depot_registrar))
    template = templates[0]
    if not os.path.isabs(location):
        location = os.path.abspath(location)
    click.echo('Upgrading existing project from {} on {} at {}'.format(template.version, template.depot, location))
    local.upgrade_project(identifier=template, dest=location, pros_cli=cfg.pros_cfg)


@conduct.command('register', aliases=[], help='Manifest project.pros file')
@click.argument('location')
@click.argument('kernel', default='latest')
@default_cfg
def register(cfg, location, kernel):
    first_run(cfg)
    kernel_version = kernel
    if kernel_version == 'latest':
        templates = local.get_local_templates(pros_cfg=cfg.pros_cfg,
                                              template_types=[TemplateTypes.kernel])  # type: List[Identifier]
        if not templates or len(templates) == 0:
            click.echo('No templates have been downloaded! Use `pros conduct download` to download the latest kernel or'
                       ' specify a kernel manually.')
            click.get_current_context().abort()
            sys.exit()
        kernel_version = sorted(templates, key=lambda t: semver.Version(t.version))[-1].version
        proscli.utils.debug('Resolved version {} to {}'.format(kernel, kernel_version))

    cfg = prosconfig.ProjectConfig(location, create=True, raise_on_error=True)
    cfg.kernel = kernel_version
    click.echo('Registering {} with kernel {}'.format(location, kernel_version))
    cfg.save()
# endregion


@conduct.command('first-run', help='Runs the first-run configuration')
@click.option('--no-force', is_flag=True, default=True)
@click.option('--use-defaults', is_flag=True, default=False)
@default_cfg
def first_run_cmd(cfg, no_force, use_defaults):
    first_run(cfg, force=no_force, defaults=use_defaults)
