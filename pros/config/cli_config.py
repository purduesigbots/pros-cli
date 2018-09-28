import json.decoder
import os.path
from datetime import datetime, timedelta
from typing import *

import click

import pros.common
# import pros.conductor.providers.github_releases as githubreleases
from pros.config.config import Config

if TYPE_CHECKING:
    from pros.upgrade.manifests.upgrade_manifest_v1 import UpgradeManifestV1  # noqa: F401


class CliConfig(Config):
    def __init__(self, file=None):
        if not file:
            file = os.path.join(click.get_app_dir('PROS'), 'cli.pros')
        self.update_frequency: timedelta = timedelta(hours=1)
        self.override_use_build_compile_commands: Optional[bool] = None
        self.offer_sentry: Optional[bool] = None

        super(CliConfig, self).__init__(file)

    def needs_online_fetch(self, last_fetch: datetime) -> bool:
        return datetime.now() - last_fetch > self.update_frequency

    @property
    def use_build_compile_commands(self):
        if self.override_use_build_compile_commands is not None:
            return self.override_use_build_compile_commands
        paths = [os.path.join('~', '.pros-atom'), os.path.join('~', '.pros-editor')]
        return any([os.path.exists(os.path.expanduser(p)) for p in paths])

    def get_upgrade_manifest(self, force: bool = False) -> Optional['UpgradeManifestV1']:
        from pros.upgrade.manifests.upgrade_manifest_v1 import UpgradeManifestV1  # noqa: F811

        if not force and not self.needs_online_fetch(self.cached_upgrade[0]):
            return self.cached_upgrade[1]
        pros.common.logger(__name__).info('Fetching upgrade manifest...')
        import requests
        import jsonpickle
        r = requests.get('https://purduesigbots.github.io/pros-mainline/cli-updates.json')
        pros.common.logger(__name__).debug(r)
        if r.status_code == 200:
            try:
                self.cached_upgrade = (datetime.now(), jsonpickle.decode(r.text))
            except json.decoder.JSONDecodeError:
                return None
            assert isinstance(self.cached_upgrade[1], UpgradeManifestV1)
            pros.common.logger(__name__).debug(self.cached_upgrade[1])
            self.save()
            return self.cached_upgrade[1]
        else:
            pros.common.logger(__name__).warning(f'Failed to fetch CLI updates because status code: {r.status_code}')
            pros.common.logger(__name__).debug(r)
            return None


def cli_config() -> CliConfig:
    ctx = click.get_current_context(silent=True)
    if not ctx or not isinstance(ctx, click.Context):
        return CliConfig()
    ctx.ensure_object(dict)
    assert isinstance(ctx.obj, dict)
    if not hasattr(ctx.obj, 'cli_config') or not isinstance(ctx.obj['cli_config'], CliConfig):
        ctx.obj['cli_config'] = CliConfig()
    return ctx.obj['cli_config']
