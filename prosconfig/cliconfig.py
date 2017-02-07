import click
import os.path
import prosconductor.providers.githubreleases
import sys
from prosconfig import Config


class CliConfig(Config):
    def __init__(self, file=None, ctx=None):
        if not file:
            file = os.path.join(click.get_app_dir('PROS'), 'cli.pros')
        self.default_libraries = []  # type: list(str)
        self.providers = []
        self.applyDefaultProviders()
        super(CliConfig, self).__init__(file, ctx=ctx)

    def applyDefaultProviders(self):
        if os.path.isfile(prosconductor.providers.githubreleases.__file__):
            self.providers.append(prosconductor.providers.githubreleases.__file__)
        elif hasattr(sys, 'frozen'):
            self.providers.append(os.path.join(os.path.dirname(sys.executable), 'githubreleases.pyc'))
