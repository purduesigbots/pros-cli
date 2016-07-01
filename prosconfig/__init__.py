import os
import os.path
import json
import ntpath
import click

import prosconductor.updatesite.ftpprovider
import prosconductor.updatesite.localprovider
import prosconductor.updatesite


# this file contains all of the various config files classes, including the global config file,
# per project config, and kernel template config file

def get_state():
    return click.get_current_context().obj


class Config(object):
    class Encoder(json.JSONEncoder):
        def default(self, o):
            if not isinstance(o, object):
                return super(Config.Encoder, self).default(o)
            d = o.__dict__
            for attr in o.__dict__.keys():
                if hasattr(o.__getattribute__(attr), '__dict__'):
                    d[attr] = self.default(o)
            return d

    class Decoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            super(Config.Decoder, self).__init__(object_hook=self.object_hook, *args, **kwargs)

        @staticmethod
        def object_hook(d):
            if not isinstance(d, dict):
                return d
            if 'update_sites' in d:
                sites = d['update_sites']
                d['update_sites'] = set()
                for site in sites:
                    d['update_sites'].append(prosconductor.updatesite.UpdateSite(d=site))
            return d

    def __init__(self, file):
        if os.path.isfile(file):
            with open(file, 'r') as f:
                self.__dict__ = json.loads(f.read(), cls=Config.Decoder)
        if not os.path.isdir(file):
            self.path = ntpath.split(file)[:-1][0]
            self.save_path = file
        self.__ignored = ['_Config__ignored', 'path', 'save_path']

    def save(self, file=None):
        if file is None:
            file = self.save_path
        dictionary = {k: self.__dict__[k] for k in self.__dict__ if k not in self.__ignored}
        os.makedirs(ntpath.split(file)[:-1][0], exist_ok=True)
        with open(file, 'w') as f:
            f.write(json.dumps(dictionary, indent=True, cls=Config.Encoder))
        pass

    def __repr__(self):
        return '{}: {}'.format(type(self).__name__, repr(self.__dict__))


class ProjectConfig(Config):
    def __init__(self, file):
        super(ProjectConfig, self).__init__(file)
        if 'kernel' not in self.__dict__:
            self.kernel = None
        if 'dropins' not in self.__dict__:
            self.dropins = []
        if 'output' not in self.__dict__:
            self.output = 'bin/output.bin'


class ProsConfig(Config):
    def __init__(self, file=os.path.join(click.get_app_dir('PROS'), 'config.json')):
        super(ProsConfig, self).__init__(file)
        if 'update_sites' not in self.__dict__:
            self.update_sites = {
                prosconductor.updatesite.UpdateSite(
                    uri=click.get_app_dir('PROS'),
                    registrar=prosconductor.updatesite.localprovider.LocalProvider.get_key(),
                    id='default-cache'),
                prosconductor.updatesite.UpdateSite(
                    uri='ftp://ftp.pros.rocks',
                    registrar=prosconductor.updatesite.ftpprovider.FtpProvider.get_key(),
                    id='main')
            }
        if 'default_dropins' not in self.__dict__:
            self.default_dropins = []
        if 'providers' not in self.__dict__:
            self.providers = [prosconductor.updatesite.ftpprovider.__file__,
                              prosconductor.updatesite.localprovider.__file__]


def find_project(path):
    search_dir = path
    for n in range(10):
        files = [f for f in os.listdir(search_dir)
                 if os.path.isfile(os.path.join(search_dir, f)) and f == 'pros.config']
        if len(files) == 1:  # we found a pros.config file
            pros_cfg = ProjectConfig(os.path.join(search_dir, files[0]))
            return pros_cfg
        search_dir = ntpath.split(search_dir)[:-1][0]  # move to parent dir
    return None


class KernelConfig(Config):
    def __init__(self, file):
        super(KernelConfig, self).__init__(file)
        if 'kernel' not in self.__dict__:
            self.kernel = ntpath.split(file)[-2]
        if 'dropins' not in self.__dict__:
            self.dropins = []
        if 'output' not in self.__dict__:
            self.output = 'bin/output.bin'
        if 'upgrade_files' not in self.__dict__:
            self.upgrade_files = [
                'firmware/*'
            ]
        if 'exclude_files' not in self.__dict__:
            self.exclude_files = []
        if 'loader' not in self.__dict__:
            self.loader = None
