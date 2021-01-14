import os.path

import pros.common.ui as ui
import pros.conductor as c
from pros.cli.common import *
from pros.conductor.templates import ExternalTemplate


@pros_root
def conductor_cli():
    pass


@conductor_cli.group(cls=PROSGroup, aliases=['cond', 'c', 'conduct'], short_help='Perform project management for PROS')
@default_options
def conductor():
    """
    Conductor is PROS's project management facility. It is responsible for obtaining
    templates for which to create projects from.

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
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

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """

    template_file = None
    if os.path.exists(query.identifier):
        template_file = query.identifier
    elif os.path.exists(query.name) and query.version is None:
        template_file = query.name
    elif query.metadata.get('origin', None) == 'local':
        if 'location' not in query.metadata:
            logger(__name__).error('--location option is required for the local depot. Specify --location <file>')
            logger(__name__).debug(f'Query options provided: {query.metadata}')
            return -1
        template_file = query.metadata['location']

    if template_file and (os.path.splitext(template_file)[1] in ['.zip'] or
                          os.path.exists(os.path.join(template_file, 'template.pros'))):
        template = ExternalTemplate(template_file)
        query.metadata['location'] = template_file
        depot = c.LocalDepot()
        logger(__name__).debug(f'Template file found: {template_file}')
    else:
        if template_file:
            logger(__name__).debug(f'Template file exists but is not a valid template: {template_file}')
        template = c.Conductor().resolve_template(query, allow_offline=False)
        logger(__name__).debug(f'Template from resolved query: {template}')
        if template is None:
            logger(__name__).error(f'There are no templates matching {query}!')
            return -1
        depot = c.Conductor().get_depot(template.metadata['origin'])
        logger(__name__).debug(f'Found depot: {depot}')
    # query.metadata contain all of the extra args that also go to the depot. There's no way for us to determine
    # whether the arguments are for the template or for the depot, so they share them
    logger(__name__).debug(f'Additional depot and template args: {query.metadata}')
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
@click.option('--remove-empty-dirs/--no-remove-empty-dirs', 'remove_empty_directories', is_flag=True, default=True,
              help='Remove empty directories when removing files')
@project_option()
@template_query(required=True)
@default_options
def apply(project: c.Project, query: c.BaseTemplate, **kwargs):
    """
    Upgrade or install a template to a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    return c.Conductor().apply_template(project, identifier=query, **kwargs)


@conductor.command(aliases=['i', 'in'], context_settings={'ignore_unknown_options': True})
@click.option('--upgrade/--no-upgrade', 'upgrade_ok', default=False)
@click.option('--download/--no-download', 'download_ok', default=True)
@click.option('--force-user', 'force_user', default=False, is_flag=True,
              help='Replace all user files in a template')
@click.option('--force-system', '-f', 'force_system', default=False, is_flag=True,
              help="Force all system files to be inserted into the project")
@click.option('--force-apply', 'force_apply', default=False, is_flag=True,
              help="Force apply the template, disregarding if the template is already installed.")
@click.option('--remove-empty-dirs/--no-remove-empty-dirs', 'remove_empty_directories', is_flag=True, default=True,
              help='Remove empty directories when removing files')
@project_option()
@template_query(required=True)
@default_options
@click.pass_context
def install(ctx: click.Context, **kwargs):
    """
    Install a library into a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    return ctx.invoke(apply, install_ok=True, **kwargs)


@conductor.command(context_settings={'ignore_unknown_options': True}, aliases=['u'])
@click.option('--install/--no-install', 'install_ok', default=False)
@click.option('--download/--no-download', 'download_ok', default=True)
@click.option('--force-user', 'force_user', default=False, is_flag=True,
              help='Replace all user files in a template')
@click.option('--force-system', '-f', 'force_system', default=False, is_flag=True,
              help="Force all system files to be inserted into the project")
@click.option('--force-apply', 'force_apply', default=False, is_flag=True,
              help="Force apply the template, disregarding if the template is already installed.")
@click.option('--remove-empty-dirs/--no-remove-empty-dirs', 'remove_empty_directories', is_flag=True, default=True,
              help='Remove empty directories when removing files')
@project_option()
@template_query(required=False)
@default_options
@click.pass_context
def upgrade(ctx: click.Context, project: c.Project, query: c.BaseTemplate, **kwargs):
    """
    Upgrade a PROS project or one of its libraries

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    if not query.name:
        for template in project.templates.keys():
            click.secho(f'Upgrading {template}', color='yellow')
            q = c.BaseTemplate.create_query(name=template, target=project.target,
                                            supported_kernels=project.templates['kernel'].version)
            ctx.invoke(apply, upgrade_ok=True, project=project, query=q, **kwargs)
    else:
        ctx.invoke(apply, project=project, query=query, upgrade_ok=True, **kwargs)


@conductor.command('uninstall')
@click.option('--remove-user', is_flag=True, default=False, help='Also remove user files')
@click.option('--remove-empty-dirs/--no-remove-empty-dirs', 'remove_empty_directories', is_flag=True, default=True,
              help='Remove empty directories when removing files')
@project_option()
@template_query()
@default_options
def uninstall_template(project: c.Project, query: c.BaseTemplate, remove_user: bool,
                       remove_empty_directories: bool = False):
    """
    Uninstall a template from a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    c.Conductor().remove_template(project, query, remove_user=remove_user,
                                  remove_empty_directories=remove_empty_directories)


@conductor.command('new-project', aliases=['new', 'create-project'])
@click.argument('path', type=click.Path())
@click.argument('target', default=c.Conductor().default_target, type=click.Choice(['v5', 'cortex']))
@click.argument('version', default='latest')
@click.option('--force-user', 'force_user', default=False, is_flag=True,
              help='Replace all user files in a template')
@click.option('--force-system', '-f', 'force_system', default=False, is_flag=True,
              help="Force all system files to be inserted into the project")
@click.option('--force-refresh', is_flag=True, default=False, show_default=True,
              help='Force update all remote depots, ignoring automatic update checks')
@click.option('--no-default-libs', 'no_default_libs', default=False, is_flag=True,
              help='Do not install any default libraries after creating the project.')
@click.option('--compile-after', is_flag=True, default=True, show_default=True,
              help='Compile the project after creation')
@click.option('--build-cache', is_flag=True, default=None, show_default=False,
              help='Build compile commands cache after creation. Overrides --compile-after if both are specified.')
@click.pass_context
@default_options
def new_project(ctx: click.Context, path: str, target: str, version: str,
                force_user: bool = False, force_system: bool = False,
                no_default_libs: bool = False, compile_after: bool = True, build_cache: bool = None, **kwargs):
    """
    Create a new PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    if version.lower() == 'latest' or not version:
        version = '>0'
    if not force_system and c.Project.find_project(path) is not None:
        logger(__name__).error('A project already exists in this location! Delete it first', extra={'sentry': False})
        ctx.exit(-1)
    try:
        _conductor = c.Conductor()
        if target is None:
            target = _conductor.default_target
        project = _conductor.new_project(path, target=target, version=version,
                                         force_user=force_user, force_system=force_system,
                                         no_default_libs=no_default_libs, **kwargs)
        ui.echo('New PROS Project was created:', output_machine=False)
        ctx.invoke(info_project, project=project)

        if compile_after or build_cache:
            with ui.Notification():
                ui.echo('Building project...')
                ctx.exit(project.compile([], scan_build=build_cache))

    except Exception as e:
        pros.common.logger(__name__).exception(e)
        ctx.exit(-1)


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
def query_templates(ctx, query: c.BaseTemplate, allow_offline: bool, allow_online: bool, force_refresh: bool,
                    limit: int):
    """
    Query local and remote templates based on a spec

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    if limit < 0:
        limit = 15
    templates = c.Conductor().resolve_templates(query, allow_offline=allow_offline, allow_online=allow_online,
                                                force_refresh=force_refresh)[:limit]

    render_templates = {}
    for template in templates:
        key = (template.identifier, template.origin)
        if key in render_templates:
            if isinstance(template, c.LocalTemplate):
                render_templates[key]['local'] = True
        else:
            render_templates[key] = {
                'name': template.name,
                'version': template.version,
                'location': template.origin,
                'target': template.target,
                'local': isinstance(template, c.LocalTemplate)
            }
    import semantic_version as semver
    render_templates = sorted(render_templates.values(), key=lambda k: k['local'])  # tertiary key
    render_templates = sorted(render_templates, key=lambda k: semver.Version(k['version']),
                              reverse=True)  # secondary key
    render_templates = sorted(render_templates, key=lambda k: k['name'])  # primary key
    ui.finalize('template-query', render_templates)


@conductor.command('info-project')
@click.option('--ls-upgrades/--no-ls-upgrades', 'ls_upgrades', default=False)
@project_option()
@default_options
def info_project(project: c.Project, ls_upgrades):
    """
    Display information about a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """

    from pros.conductor.project import ProjectReport
    report = ProjectReport(project)
    _conductor = c.Conductor()
    if ls_upgrades:
        for template in report.project['templates']:
            import semantic_version as semver
            templates = _conductor.resolve_templates(c.BaseTemplate.create_query(name=template["name"],
                                                                                 version=f'>{template["version"]}',
                                                                                 target=project.target))
            template["upgrades"] = sorted({t.version for t in templates}, key=lambda v: semver.Version(v), reverse=True)

    ui.finalize('project-report', report)
