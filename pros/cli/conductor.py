import os.path

import pros.common as p
import pros.conductor as c
from pros.cli.common import *
from pros.conductor.templates import ExternalTemplate


@click.group(cls=PROSGroup)
def conductor_cli():
    pass


@conductor_cli.group(cls=PROSGroup, aliases=['cond', 'c', 'conduct'], short_help='Perform project management for PROS')
@default_options
def conductor():
    """
    Conductor is PROS's project management facility. It is responsible for obtaining
    templates for which to create projects from.

    Visit https://pros.cs.purdue.edu/v5/cli/conductor to learn more
    """
    pass


@conductor.command(aliases=['download'], short_help='Fetch/Download a remote template',
                   context_settings={'ignore_unknown_options': True})
@template_query(required=True)
@default_options
def fetch(query: c.BaseTemplate):
    """
    Fetch/download a template from a depot.

    Only a template spec is required. A template spec is the name and version
    of the template formatted as name@version (libblrs@1.0.0). Semantic version
    ranges are accepted (e.g., libblrs@^1.0.0). The version parameter is also
    optional (e.g., libblrs)

    Additional parameters are available according to the depot.

    Visit https://pros.cs.purdue.edu/v5/cli/conductor to learn more
    """
    if query.metadata.get('origin', None) == 'local':
        # all of the depot/non-specific options are placed in the query metadata due to the non-determinism of where
        # the option actually belongs to
        if 'location' not in query.metadata:
            logger(__name__).error('--location option is required for the local depot. Specify --location <file>')
            return -1
        template = ExternalTemplate(query.metadata['location'])
        depot = c.LocalDepot()
    else:
        template = c.Conductor().resolve_template(query, allow_offline=False)
        logger(__name__).debug(template)
        depot = c.Conductor().get_depot(template.metadata['origin'])
    # query.metadata contain all of the extra args that also go to the depot. There's no way for us to determine
    # whether the arguments are for the template or for the depot, so they share them
    c.Conductor().fetch_template(depot, template, **query.metadata)


@conductor.command(context_settings={'ignore_unknown_options': True})
@click.option('--upgrade/--no-upgrade', 'upgrade_ok', default=True, help='Allow upgrading templates in a project')
@click.option('--install/--no-install', 'install_ok', default=True, help='Allow installing templates in a project')
@click.option('--download/--no-download', 'download_ok', default=True,
              help='Allow downloading templates or only allow local templates')
@click.option('--upgrade-user-files/--no-upgrade-user-files', 'force_user', default=False,
              help='Replace all user files in a template')
@click.option('--force', 'force_system', default=False, is_flag=True,
              help="Force all system files to be inserted into the project")
@click.option('--force-apply', 'force_apply', default=False, is_flag=True,
              help="Force apply the template, disregarding if the template is already installed.")
@project_option()
@template_query(required=True)
@default_options
def apply(project: c.Project, query: c.BaseTemplate, **kwargs):
    """
    Upgrade or install a template to a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor to learn more
    """
    c.Conductor().apply_template(project, identifier=query, **kwargs)


@conductor.command(aliases=['i', 'in'], context_settings={'ignore_unknown_options': True})
@click.option('--upgrade/--no-upgrade', 'upgrade_ok', default=False)
@click.option('--download/--no-download', 'download_ok', default=True)
@click.option('--force-user', 'force_user', default=False, is_flag=True,
              help='Replace all user files in a template')
@click.option('--force-system', '-f', 'force_system', default=False, is_flag=True,
              help="Force all system files to be inserted into the project")
@click.option('--force-apply', 'force_apply', default=False, is_flag=True,
              help="Force apply the template, disregarding if the template is already installed.")
@project_option()
@template_query(required=True)
@default_options
@click.pass_context
def install(ctx: click.Context, **kwargs):
    """
    Install a library into a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor to learn more
    """
    ctx.invoke(apply, install_ok=True, **kwargs)


@conductor.command(context_settings={'ignore_unknown_options': True})
@click.option('--install/--no-install', 'install_ok', default=False)
@click.option('--download/--no-download', 'download_ok', default=True)
@click.option('--force-user', 'force_user', default=False, is_flag=True,
              help='Replace all user files in a template')
@click.option('--force-system', '-f', 'force_system', default=False, is_flag=True,
              help="Force all system files to be inserted into the project")
@click.option('--force-apply', 'force_apply', default=False, is_flag=True,
              help="Force apply the template, disregarding if the template is already installed.")
@project_option()
@template_query(required=False)
@default_options
@click.pass_context
def upgrade(ctx: click.Context, project: c.Project, query: c.BaseTemplate, **kwargs):
    """
    Upgrade a PROS project or one of its libraries

    Visit https://pros.cs.purdue.edu/v5/cli/conductor to learn more
    """
    if not query.name:
        for template in project.templates.keys():
            click.secho(f'Upgrading {template}', color='yellow')
            q = c.BaseTemplate.create_query(name=template)
            ctx.invoke(apply, upgrade_ok=True, project=project, query=q, **kwargs)
    else:
        ctx.invoke(apply, upgrade_ok=True, **kwargs)


@conductor.command('new-project', aliases=['new', 'create-project'])
@click.argument('path', type=click.Path())
@click.argument('platform', default='v5', type=click.Choice(['v5', 'cortex']))
@click.argument('version', default='latest')
@click.option('--force-user', 'force_user', default=False, is_flag=True,
              help='Replace all user files in a template')
@click.option('--force-system', '-f', 'force_system', default=False, is_flag=True,
              help="Force all system files to be inserted into the project")
@click.option('--force-refresh', is_flag=True, default=False, show_default=True,
              help='Force update all remote depots, ignoring automatic update checks')
@click.pass_context
@default_options
def new_project(ctx: click.Context, path: str, platform: str, version: str,
                force_user: bool = False, force_system: bool = False, **kwargs):
    """
    Create a new PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor to learn more
    """
    if version.lower() == 'latest' or not version:
        version = '>0'
    if not force_system and c.Project.find_project(path) is not None:
        pros.common.logger(__name__).error('A project already exists in this location! Delete it first')
        return -1
    try:
        project = c.Conductor().new_project(path, target=platform, version=version,
                                            force_user=force_user, force_system=force_system, **kwargs)
        click.echo('New PROS Project was created:')
        ctx.invoke(info_project, project=project)
    except Exception as e:
        pros.common.logger(__name__).exception(e)
        return -1


@conductor.command('query-templates',
                   aliases=['search-templates', 'ls-templates', 'lstemplates', 'querytemplates', 'searchtemplates'],
                   context_settings={'ignore_unknown_options': True})
@click.option('--allow-offline/--no-offline', 'allow_offline', default=True, show_default=True,
              help='(Dis)allow offline templates in the listing')
@click.option('--allow-online/--no-online', 'allow_online', default=True, show_default=True,
              help='(Dis)allow online templates in the listing')
@click.option('--force-refresh', is_flag=True, default=False, show_default=True,
              help='Force update all remote depots, ignoring automatic update checks')
@click.option('--limit', type=int, default=15, help='Limit displayed results.')
@template_query(required=False)
@click.pass_context
@default_options
def query_templates(ctx, query: c.BaseTemplate, allow_offline: bool, allow_online: bool, force_refresh: bool, limit: int):
    """
    Query local and remote templates based on a spec

    Visit https://pros.cs.purdue.edu/v5/cli/conductor to learn more
    """
    if limit < 0:
        limit = 15
    templates = c.Conductor().resolve_templates(query, allow_offline=allow_offline, allow_online=allow_online,
                                                force_refresh=force_refresh)[:limit]
    if ismachineoutput(ctx):
        import jsonpickle
        if isdebug(__name__):
            jsonpickle.set_encoder_options('json', sort_keys=True)
        click.echo(jsonpickle.encode(templates, unpicklable=False))
    else:
        import tabulate
        templates = [
            (t.name, t.version, t.metadata.get('origin', 'Unknown'), 'yes' if isinstance(t, c.LocalTemplate) else 'no')
            for t in templates]
        click.echo(tabulate.tabulate(templates, headers=('Name', 'Version', 'Origin', 'Local')))


@conductor.command('info-project')
@project_option()
@default_options
def info_project(project: c.Project):
    """
    Display information about a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor to learn more
    """
    if ismachineoutput():
        import jsonpickle
        if isdebug(__name__):
            jsonpickle.set_encoder_options('json', sort_keys=True)
        click.echo(jsonpickle.encode(project, unpicklable=False))
    else:
        import tabulate
        click.echo(f'PROS Project for {project.target} at: {os.path.abspath(project.location)}' +
                   f' ({project.name})' if project.name else '')
        templates = [(t.name, t.version, t.metadata.get('origin', 'Unknown')) for t in project.templates.values()]
        if any(templates):
            click.echo('Installed Templates:')
            click.echo(tabulate.tabulate(templates, headers=('Name', 'Version', 'Origin')))
        else:
            click.echo('No templates are part of this project.')
