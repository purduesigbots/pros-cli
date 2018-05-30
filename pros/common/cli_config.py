import os.path

import click

# import pros.conductor.providers.github_releases as githubreleases
from pros.config.config import Config


class CliConfig(Config):
    def __init__(self, file=None):
        if not file:
            file = os.path.join(click.get_app_dir('PROS'), 'cli.pros')
        # right now, CliConfig is pretty barebones. JINX and terminal may eventually use these to control
        # default port selection

        super(CliConfig, self).__init__(file)


def cli_config() -> CliConfig:
    ctx = click.get_current_context(silent=True)
    ctx.ensure_object(dict)
    assert isinstance(ctx.obj, dict)
    if not hasattr(ctx.obj, 'cli_config') or not isinstance(ctx.obj['cli_config'], CliConfig):
        ctx.obj['cli_config'] = CliConfig()
    return ctx.obj['cli_config']
