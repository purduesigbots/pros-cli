import sys
import urllib
import zipfile

import prosconductor
from prosconductor import updatesite

__update_site_providers = {updatesite.UrlUpdateSiteProvider}


def register_update_site_provider(provider):
    __update_site_providers.add(provider)


def find_update_site_provider(uri):
    for provider in __update_site_providers:
        if prosconductor.verbosity > 2:
            print('Checking claimability of ', provider)
        if provider().claims_uri(uri):
            return provider

    for provider in __update_site_providers:
        if prosconductor.verbosity > 2:
            print('Checking handleability of ', provider)
        if provider().can_handle_uri(uri):
            return provider

    return updatesite.DefaultUpdateSiteProvider
