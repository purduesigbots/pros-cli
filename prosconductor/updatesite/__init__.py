import importlib.util
import re
import prosconfig
from prosconductor.updatesite.genericprovider import UpdateSiteProvider
from cachetools.func import ttl_cache
import proscli.utils


def get_all_providers(proj_cfg=None):
    if proj_cfg is None:
        proj_cfg = prosconfig.get_state().proj_cfg
    for provider_file in proj_cfg.providers:
        # loads module based on filename... implementation based on http://stackoverflow.com/a/67692
        spec = importlib.util.spec_from_file_location('module.name', provider_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    return {x.get_key(): x for x in UpdateSiteProvider.__subclasses__()}


@ttl_cache(maxsize=10, ttl=60.0)
def get_kernels(*, site_pattern='.*', key_pattern='.*', sites=None):
    proscli.utils.debug('Finding all kernels')
    if sites is None:
        sites = prosconfig.get_state().proj_cfg.update_sites

    d = dict()
    for site in [s for s in sites if re.match(site_pattern, s.uri) and re.match(key_pattern, s.registrar)]:
        for k in site.get_kernels():
            if k not in d:
                d[k] = set()
            d[k].add(site)
    return d

    # this is basically magic. http://stackoverflow.com/a/952952
    # return {kernel for site in sites if re.match(site_pattern, site.uri) and re.match(key_pattern, site.registrar)
    #         for kernel in site.get_kernels()}


class UpdateSite(object):
    def __init__(self, uri=None, registrar=None, registrar_options=None, id=None, d=None):
        if isinstance(d, dict):
            self.__dict__ = d
        else:
            if registrar_options is None:
                registrar_options = dict()
            self.uri = uri
            self.registrar = registrar
            self.id = id
            self.registrar_options = registrar_options

    @ttl_cache(ttl=60.0)
    def get_kernels(self):
        providers = get_all_providers()
        if self.registrar in providers:
            return providers[self.registrar].get_kernels(self)
        else:
            return []

    def __hash__(self):
        return self.id.__hash__()
