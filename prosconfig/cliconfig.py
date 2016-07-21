import click
import os.path
import prosconductor.providers.githubreleases
import proscli.utils
from prosconfig import Config


class CliConfig(Config):
    def __init__(self, file: str=None, ctx=None):
        if not file:
            file = os.path.join(click.get_app_dir('PROS'), 'cli.pros')
        self.default_libraries = []  # type: list(str)
        self.providers = [
            prosconductor.providers.githubreleases.__file__
        ]  # type: list(str)
        super(CliConfig, self).__init__(file, ctx=ctx)
