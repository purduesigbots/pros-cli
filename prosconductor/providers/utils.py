import importlib.util
import os
from prosconductor.providers import DepotProvider, DepotConfig, TemplateTypes, Identifier, TemplateDescriptor
from prosconfig.cliconfig import CliConfig
from typing import Dict, List


def get_all_provider_types(pros_cfg: CliConfig = None) -> Dict[str, type]:
    if pros_cfg is None:
        pros_cfg = CliConfig()

    for provider_file in pros_cfg.providers:
        spec = importlib.util.spec_from_file_location('module.name', provider_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    return {x.registrar: x for x in DepotProvider.__subclasses__()}


def get_provider(depot: DepotConfig,
                 pros_cfg: CliConfig = None
                 ) -> DepotProvider:
    providers = get_all_provider_types(pros_cfg)
    if depot.registrar in providers:
        return providers[depot.registrar](depot)
    else:
        return None


def get_all_depot_configs(pros_cfg: CliConfig = None) -> List[DepotConfig]:
    if pros_cfg is None:
        pros_cfg = CliConfig()

    result = list()  # type: List[prosconductor.providers.DepotConfig]
    for dir in [os.path.join(pros_cfg.directory, d) for d in os.listdir(pros_cfg.directory)
                if os.path.isdir(os.path.join(pros_cfg.directory, d))]:
        if 'depot.pros' in os.listdir(dir):
            result.append(DepotConfig(os.path.join(dir, 'depot.pros')))

    return result


def get_all_depots(pros_cfg: CliConfig = None) -> List[DepotProvider]:
    if pros_cfg is None:
        pros_cfg = CliConfig()

    return [get_provider(depot, pros_cfg) for depot in get_all_depot_configs(pros_cfg)]


def get_all_available_templates(pros_cfg: CliConfig = None, template_types: List[TemplateTypes] = None) \
        -> Dict[TemplateTypes, Dict[Identifier, List[TemplateDescriptor]]]:
    if pros_cfg is None:
        pros_cfg = CliConfig()
    if template_types is None:
        template_types = [TemplateTypes.kernel, TemplateTypes.library]

    result = dict()  # type: Dict[TemplateTypes, Dict[Identifier, List[TemplateDescriptor]]]
    for template_type in template_types:
        result[template_type] = dict()

    for depot in get_all_depots(pros_cfg):
        if bool(depot.config.types) and not bool([t for t in template_types if t in depot.config.types]):
            continue  # No intersection between the types declared by the depot and requested types
        templates = dict()
        offline = depot.list_local(template_types)
        online = depot.list_all(template_types)
        for key in [k for k in offline if k in online]:
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
