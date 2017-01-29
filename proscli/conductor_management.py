from proscli.conductor import conduct, first_run
from prosconductor.providers import TemplateTypes, Identifier, TemplateConfig
import click
import json
from proscli.utils import default_cfg
import prosconductor.providers.local as local
import prosconductor.providers.utils as utils
import prosconfig
import semantic_version as semver
import jsonpickle

# Commands in this module are typically for automation/IDE purposes and probably won't be used by front-end users


@conduct.command('create-template', short_help='Creates a template with the specified name, version, and depot')
@click.argument('name')
@click.argument('version')
@click.argument('depot')
@click.option('--location')
@click.option('--ignore', '-i', multiple=True)
@click.option('--upgrade-files', '-u', multiple=True)
@default_cfg
def create_template(cfg, name, version, depot, location, ignore, upgrade_files):
    first_run(cfg)
    template = local.create_template(utils.Identifier(name, version, depot), location=location)
    template.template_ignore = ignore
    template.upgrade_paths = upgrade_files
    template.save()
    click.echo(jsonpickle.encode(template))
    click.echo('Created template at {}'.format(template.save_file))


@conduct.command('info-project', help='Provides information about a project. Especially useful for IDEs')
@click.argument('location')
@default_cfg
def info_project(cfg, location):
    project = prosconfig.ProjectConfig(path=location)
    details = dict()
    details['kernel'] = project.kernel
    templates = local.get_local_templates(pros_cfg=cfg.pros_cfg, template_types=[TemplateTypes.kernel])
    details['kernelUpToDate'] = semver.compare(project.kernel,
                                               sorted(templates, key=lambda t: semver.Version(t.version))[-1].version) \
                                >= 0
    templates = local.get_local_templates(pros_cfg=cfg.pros_cfg, template_types=[TemplateTypes.library])
    details['libraries'] = dict()
    if project.libraries.__class__ is dict:
        for (lib, ver) in project.libraries.items():
            details['libraries'][lib] = dict()
            details['libraries'][lib]['version'] = ver
            sorted_versions = sorted([t.version for t in templates if t.name == lib], key=lambda v: semver.Version(v))
            if len(sorted_versions) > 0:
                latest = semver.compare(ver, sorted_versions[-1]) >= 0
            else:
                latest = True
            details['libraries'][lib]['latest'] = latest
    click.echo(json.dumps(details))


@conduct.command('ls-registrars', help='List available registrars')
@default_cfg
def ls_registrars(cfg):
    table = {
        key: {'location_desc': value.location_desc, 'config': value.config} for key, value in utils.get_all_provider_types().items()
        }
    click.echo(json.dumps(table))


@conduct.command('info-depot', help='Get config for a depot')
@click.argument('depot')
@default_cfg
def info_depot(cfg, depot):
    dpt = utils.get_depot_config(depot)
    if dpt is None:
        click.echo(json.dumps(dict()))
    else:
        click.echo(json.dumps(dpt.registrar_options))


@conduct.command('set-depot-key', help='Set a config key/value pair for a depot')
@click.argument('depot')
@click.argument('key')
@click.argument('value')
@default_cfg
def set_depot_key(cfg, depot, key, value):
    dpt = utils.get_depot_config(depot)
    config = utils.get_all_provider_types(cfg.pros_cfg)[dpt.registrar]
    click.echo(config)
    config = config.config
    click.echo(config)
    if dpt is None:
        pass
    if config.get(key, dict()).get('method', 'str') == 'bool':
        value = value in ['true', 'True', 'TRUE', '1', 't', 'y', 'yes']
    dpt.registrar_options[key] = value
    dpt.save()
