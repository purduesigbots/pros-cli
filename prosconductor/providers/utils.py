from functools import lru_cache
import importlib.util
import importlib.abc
import os
import re
from prosconductor.providers import DepotProvider, DepotConfig, TemplateTypes, Identifier, TemplateDescriptor
from prosconfig.cliconfig import CliConfig
# from typing import Dict, List


@lru_cache()
def get_all_provider_types(pros_cfg=None):
    if pros_cfg is None:
        pros_cfg = CliConfig()

    for provider_file in pros_cfg.providers:
        spec = importlib.util.spec_from_file_location('prosconductor.providers.{}'.format(os.path.basename(provider_file).split('.')[0]), provider_file)
        spec.loader.load_module()

    return {x.registrar: x for x in DepotProvider.__subclasses__()}


@lru_cache()
def get_depot(depot_cfg, pros_cfg=None):
    providers = get_all_provider_types(pros_cfg)
    if depot_cfg.registrar in providers:
        return providers[depot_cfg.registrar](depot_cfg)
    else:
        return None


@lru_cache()
def get_depot_config(name, pros_cfg=None):
    if pros_cfg is None:
        pros_cfg = CliConfig()

    return DepotConfig(os.path.join(pros_cfg.directory, name, 'depot.pros'))


def get_depot_configs(pros_cfg=None, filters=None):
    if pros_cfg is None:
        pros_cfg = CliConfig()
    if filters is None or not filters:
        filters = ['.*']
    return [depot for depot in [get_depot_config(d, pros_cfg=pros_cfg) for d in os.listdir(pros_cfg.directory)
                                if os.path.isdir(os.path.join(pros_cfg.directory, d))]
            if depot.name and not all(m is None for m in [re.match(string=depot.name, pattern=f) for f in filters])]


def get_depots(pros_cfg=None, filters=None):
    return [get_depot(depot, pros_cfg) for depot in get_depot_configs(pros_cfg, filters)
            if get_depot(depot, pros_cfg) is not None]


def get_available_templates(pros_cfg=None, template_types=None,
                            filters=[], offline_only=False):
    if pros_cfg is None:
        pros_cfg = CliConfig()
    if template_types is None:
        template_types = [TemplateTypes.kernel, TemplateTypes.library]

    result = dict()  # type: Dict[TemplateTypes, Dict[Identifier, List[TemplateDescriptor]]]
    for template_type in template_types:
        result[template_type] = dict()

    for depot in [depot for depot in get_depots(pros_cfg, filters)]:
        if bool(depot.config.types) and not bool([t for t in template_types if t in depot.config.types]):
            continue  # No intersection between the types declared by the depot and requested types
        templates = dict()
        offline = depot.list_local(template_types)
        if not offline_only:
            online = depot.list_online(template_types)
        else:
            online = {t: set() for t in template_types}
        for key in [k for k in online.keys() if k in offline.keys()]:
            templates[key] = offline[key] | online[key]
        for template_type, identifiers in templates.items():
            for identifier in identifiers:
                if identifier not in result[template_type]:
                    result[template_type][identifier] = list()
                result[template_type][identifier].append(
                    TemplateDescriptor(depot=depot,
                                       online=identifier in online[template_type],
                                       offline=identifier in offline[template_type]))
    return result


