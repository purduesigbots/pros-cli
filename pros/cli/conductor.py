import os.path
from itertools import groupby

import pros.common.ui as ui
import pros.conductor as c
from pros.cli.common import *
from pros.conductor.templates import ExternalTemplate
from pros.ga.analytics import analytics


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
    analytics.send("fetch-template")
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
        else:
            logger(__name__).error(f'Template not found: {query.name}')
            return -1
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
@click.option('--early-access/--no-early-access', '--early/--no-early', '-ea/-nea', 'early_access', '--beta/--no-beta', default=None,
              help='Create a project using the PROS 4 kernel')
@project_option()
@template_query(required=True)
@default_options
def apply(project: c.Project, query: c.BaseTemplate, **kwargs):
    """
    Upgrade or install a template to a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    analytics.send("apply-template")
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
    analytics.send("install-template")
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
@click.option('--early-access/--no-early-access', '--early/--no-early', '-ea/-nea', 'early_access', '--beta/--no-beta', default=None,
              help='Create a project using the PROS 4 kernel')
@project_option()
@template_query(required=False)
@default_options
@click.pass_context
def upgrade(ctx: click.Context, project: c.Project, query: c.BaseTemplate, **kwargs):
    """
    Upgrade a PROS project or one of its libraries

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    analytics.send("upgrade-project")
    if not query.name:
        for template in tuple(project.templates.keys()):
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
@click.option('--no-make-clean', is_flag=True, default=True, help='Do not run make clean after removing')
@project_option()
@template_query()
@default_options
def uninstall_template(project: c.Project, query: c.BaseTemplate, remove_user: bool,
                       remove_empty_directories: bool = False, no_make_clean: bool = False):
    """
    Uninstall a template from a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    analytics.send("uninstall-template")
    c.Conductor().remove_template(project, query, remove_user=remove_user,
                                  remove_empty_directories=remove_empty_directories)
    if no_make_clean:
        with ui.Notification():
            project.compile(["clean"])


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
@click.option('--early-access/--no-early-access', '--early/--no-early', '-ea/-nea', 'early_access', '--beta/--no-beta', default=None,
              help='Create a project using the PROS 4 kernel')
@click.pass_context
@default_options
def new_project(ctx: click.Context, path: str, target: str, version: str,
                force_user: bool = False, force_system: bool = False,
                no_default_libs: bool = False, compile_after: bool = True, build_cache: bool = None, **kwargs):
    """
    Create a new PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    analytics.send("new-project")
    version_source = version.lower() == 'latest'
    if version.lower() == 'latest' or not version:
        version = '>0'
    if not force_system and c.Project.find_project(path) is not None:
        logger(__name__).error('A project already exists in this location at ' + c.Project.find_project(path) + 
                               '! Delete it first. Are you creating a project in an existing one?', extra={'sentry': False})
        ctx.exit(-1)
    try:
        _conductor = c.Conductor()
        if target is None:
            target = _conductor.default_target
        project = _conductor.new_project(path, target=target, version=version, version_source=version_source,
                                         force_user=force_user, force_system=force_system,
                                         no_default_libs=no_default_libs, **kwargs)
        ui.echo('New PROS Project was created:', output_machine=False)
        ctx.invoke(info_project, project=project)

        if (compile_after or build_cache) and not no_default_libs:
            with ui.Notification():
                ui.echo('Building project...')
                exit_code = project.compile([], scan_build=build_cache)
                if exit_code != 0:
                    logger(__name__).error(f'Failed to make project: Exit Code {exit_code}', extra={'sentry': False})
                    raise click.ClickException('Failed to build')

    except Exception as e:
        pros.common.logger(__name__).exception(e)
        ctx.exit(-1)


@conductor.command('query-templates',
                   aliases=['search-templates', 'ls-templates', 'lstemplates', 'querytemplates', 'searchtemplates', 'q'],
                   context_settings={'ignore_unknown_options': True})
@click.option('--allow-offline/--no-offline', 'allow_offline', default=True, show_default=True,
              help='(Dis)allow offline templates in the listing')
@click.option('--allow-online/--no-online', 'allow_online', default=True, show_default=True,
              help='(Dis)allow online templates in the listing')
@click.option('--force-refresh', is_flag=True, default=False, show_default=True,
              help='Force update all remote depots, ignoring automatic update checks')
@click.option('--limit', type=int, default=15,
              help='The maximum number of displayed results for each library')
@click.option('--early-access/--no-early-access', '--early/--no-early', '-ea/-nea', 'early_access', '--beta/--no-beta', default=None,
              help='View a list of early access templates')
@template_query(required=False)
@project_option(required=False)
@click.pass_context
@default_options
def query_templates(ctx, project: Optional[c.Project], query: c.BaseTemplate, allow_offline: bool, allow_online: bool, force_refresh: bool,
                    limit: int, early_access: bool):
    """
    Query local and remote templates based on a spec

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    analytics.send("query-templates")
    if limit < 0:
        limit = 15
    if early_access is None and project is not None:
        early_access = project.use_early_access
    templates = c.Conductor().resolve_templates(query, allow_offline=allow_offline, allow_online=allow_online,
                                                force_refresh=force_refresh, early_access=early_access)
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
    render_templates = sorted(render_templates.values(), key=lambda k: (k['name'], semver.Version(k['version']), k['local']), reverse=True)

    # Impose the output limit for each library's templates
    output_templates = []
    for _, g in groupby(render_templates, key=lambda t: t['name'] + t['target']):
        output_templates += list(g)[:limit]
    ui.finalize('template-query', output_templates)


@conductor.command('info-project')
@click.option('--ls-upgrades/--no-ls-upgrades', 'ls_upgrades', default=False)
@project_option()
@default_options
def info_project(project: c.Project, ls_upgrades):
    """
    Display information about a PROS project

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    analytics.send("info-project")    
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

@conductor.command('add-depot')
@click.argument('name')
@click.argument('url')
@default_options
def add_depot(name: str, url: str):
    """
    Add a depot

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    _conductor = c.Conductor()
    _conductor.add_depot(name, url)

    ui.echo(f"Added depot {name} from {url}")

@conductor.command('remove-depot')
@click.argument('name')
@default_options
def remove_depot(name: str):
    """
    Remove a depot

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    _conductor = c.Conductor()
    _conductor.remove_depot(name)

    ui.echo(f"Removed depot {name}")

@conductor.command('query-depots')
@click.option('--url', is_flag=True)
@default_options
def query_depots(url: bool):
    """
    Gets all the stored depots

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """
    _conductor = c.Conductor()
    ui.echo(f"Available Depots{' (Add --url for the url)' if not url else ''}:\n")
    ui.echo('\n'.join(_conductor.query_depots(url))+"\n")

@conductor.command('reset')
@click.option('--force', is_flag=True, default=False, help='Force reset')
@default_options
def reset(force: bool):
    """
    Reset conductor.pros

    Visit https://pros.cs.purdue.edu/v5/cli/conductor.html to learn more
    """

    if not force:
        if not ui.confirm("This will remove all depots and templates. You will be unable to create a new PROS project if you do not have internet connection. Are you sure you want to continue?"):
            ui.echo("Aborting")
            return
        
    # Delete conductor.pros
    file = os.path.join(click.get_app_dir('PROS'), 'conductor.pros')
    if os.path.exists(file):
        os.remove(file)

    ui.echo("Conductor was reset")
