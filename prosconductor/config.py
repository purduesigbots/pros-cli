import json
import os
from json import decoder

import prosconductor

kernel_repo = os.path.normpath(os.path.expanduser('~/.pros/kernels'))
dropin_repo = os.path.normpath(os.path.expanduser('~/.pros/dropins'))


def __init__(path=os.path.expanduser("~/.pros/cli-config.json")):
    global __payload
    global __path

    __path = path
    if os.path.isfile(__path):
        file = open(__path, 'r')
        try:
            __payload = json.load(file)
        except json.decoder.JSONDecodeError:
            __payload = json.loads('{}')
        file.close()
    else:
        __payload = json.loads('{}')

__init__()

def get_payload(self):
    return self.__payload


def get_update_sites():
    if __payload is not None and 'updateSites' in __payload:
        return __payload['updateSites']
    else:
        return dict()


def set_update_sites(sites):
    __payload['updateSites'] = sites


def add_update_site(site):
    if 'updateSites' not in __payload:
        __payload['updateSites'] = dict()
    __payload['updateSites'][site] = repr(prosconductor.updatesite.find_update_site_provider(site))


# def get_kernel_directory(self):
#     if self.__payload is not None:
#         return self.__payload['kernelDirectory']
#     else:
#         return ''
#
# def set_kernel_directory(self, new_val):
#     self.__payload['kernelDirectory'] = new_val

def serialize():
    file = open(__path, 'w')
    json.dump(__payload, file)
    file.close()
