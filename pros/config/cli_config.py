import click
import os.path
import pros.conductor.providers.github_releases as githubreleases
import sys
from .config import Config


class CliConfig(Config):
    def __init__(self, file=None, state=None):
        if not file:
            file = os.path.join(click.get_app_dir('PROS'), 'cli.pros')
        self.default_libraries = []
        self.providers = []
        super(CliConfig, self).__init__(file, state=state)

    def reset_providers(self):
        if os.path.isfile(githubreleases.__file__):
            self.providers = [githubreleases.__file__]
        elif hasattr(sys, 'frozen'):
            self.providers = [os.path.join(os.path.dirname(sys.executable), 'githubreleases.pyc')]
