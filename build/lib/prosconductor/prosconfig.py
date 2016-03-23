import json
import os

kernel_repo = os.path.normpath(os.path.expanduser('~/.pros/kernels'))
dropin_repo = os.path.normpath(os.path.expanduser('~/.pros/dropins'))


class UpdateSite:
    def __init__(self, uri, provider):
        self.uri = uri
        self.provider = provider


class ProsConfig:
    def __init__(self, path=os.path.expanduser("~/.pros/cli-config.json")):
        self.__path = path
        if os.path.isfile(self.__path):
            file = open(self.__path, 'r')
            self.__payload = json.load(file)
            file.close()
        else:
            self.__payload = json.loads('{}')

    def get_payload(self):
        return self.__payload

    def get_update_sites(self):
        if self.__payload is not None and 'updateSites' in self.__payload:
            return self.__payload['updateSites']
        else:
            return None

    def set_update_sites(self, sites):
        self.__payload['updateSites'] = sites

    def add_update_site(self, site):
        if 'updateSites' not in self.__payload:
            self.__payload['updateSites'] = []
        self.__payload['updateSites'].append(site)

    # def get_kernel_directory(self):
    #     if self.__payload is not None:
    #         return self.__payload['kernelDirectory']
    #     else:
    #         return ''
    #
    # def set_kernel_directory(self, new_val):
    #     self.__payload['kernelDirectory'] = new_val

    def serialize(self):
        file = open(self.__path, 'w')
        json.dump(self.__payload, file)
        file.close()
