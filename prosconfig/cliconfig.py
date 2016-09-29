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
        if os.path.isfile(prosconductor.providers.githubreleases.__file__):
            self.providers = [prosconductor.providers.githubreleases.__file__]
        elif hasattr(sys, 'frozen'):
            self.providers = [os.path.join(os.path.dirname(sys.executable), 'githubreleases.pyc')]
        else:
            self.providers = []
        # self.providers = [
        #     prosconductor.providers.githubreleases.__file__
        #         if os.path.isfile(prosconductor.providers.githubreleases.__file__) else
        #         os.path.join(os.path.dirname(sys.executable), 'githubreleases.pyc')
        # ]  # type: list(str)
        super(CliConfig, self).__init__(file, ctx=ctx)
