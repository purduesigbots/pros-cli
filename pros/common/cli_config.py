import os.path
import sys
from typing import *

import click

import pros.conductor.providers.github_releases as githubreleases
from pros.config.config import Config
from pros.conductor import Template


class CliConfig(Config):
    def __init__(self, file=None):
        if not file:
            file = os.path.join(click.get_app_dir('PROS'), 'cli.pros')
        self.default_libraries = []  # type: List[str]
        self.providers = []  # type: List[str]
        self.templates = []  # type: List[Template]

        super(CliConfig, self).__init__(file)

    def reset_providers(self):
        if os.path.isfile(githubreleases.__file__):
            self.providers = [githubreleases.__file__]
        elif hasattr(sys, 'frozen'):
            self.providers = [os.path.join(os.path.dirname(sys.executable), 'githubreleases.pyc')]
