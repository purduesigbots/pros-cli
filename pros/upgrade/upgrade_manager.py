import os.path
from datetime import datetime
from enum import Enum
from typing import *

from pros.common import logger
import pros.common.ui as ui
from pros.config import Config
from pros.config.cli_config import cli_config
from .manifests import *
from .instructions import UpgradeResult


class ReleaseChannel(Enum):
    Stable = 'stable'
    Beta = 'beta'


class UpgradeManager(Config):
    def __init__(self, file=None):
        if file is None:
            file = os.path.join(cli_config().directory, 'upgrade.pros.json')
        self._last_check: datetime = datetime.min
        self._manifest: Optional[UpgradeManifestV1] = None
        self.release_channel: ReleaseChannel = ReleaseChannel.Stable

        super().__init__(file)

    @property
    def has_stale_manifest(self):
        if self._manifest is None:
            logger(__name__).debug('Upgrade manager\'s manifest is nonexistent')
        if datetime.now() - self._last_check > cli_config().update_frequency:
            logger(__name__).debug(f'Upgrade manager\'s last check occured at {self._last_check}.')
            logger(__name__).debug(f'Was longer ago than update frequency ({cli_config().update_frequency}) allows.')
        return (self._manifest is None) or (datetime.now() - self._last_check > cli_config().update_frequency)

    def get_manifest(self, force: bool = False) -> UpgradeManifestV1:
        if not force and not self.has_stale_manifest:
            return self._manifest

        ui.echo('Fetching upgrade manifest...')
        import requests
        import jsonpickle
        import json

        channel_url = f'https://purduesigbots.github.io/pros-mainline/{self.release_channel.value}'
        self._manifest = None

        manifest_urls = [f"{channel_url}/{manifest.__name__}.json" for manifest in manifests]
        for manifest_url in manifest_urls:
            resp = requests.get(manifest_url)
            if resp.status_code == 200:
                try:
                    self._manifest = jsonpickle.decode(resp.text, keys=True)
                    logger(__name__).debug(self._manifest)
                    self._last_check = datetime.now()
                    self.save()
                    break
                except json.decoder.JSONDecodeError as e:
                    logger(__name__).warning(f'Failed to decode {manifest_url}')
                    logger(__name__).debug(e)
            else:
                logger(__name__).debug(f'Failed to get {manifest_url} ({resp.status_code})')
        if not self._manifest:
            manifest_list = "\n".join(manifest_urls)
            logger(__name__).warning(f'Could not access any upgrade manifests from any of:\n{manifest_list}')
        return self._manifest

    @property
    def needs_upgrade(self) -> bool:
        manifest = self.get_manifest()
        if manifest is None:
            return False
        return manifest.needs_upgrade

    def describe_update(self) -> str:
        manifest = self.get_manifest()
        assert manifest is not None
        return manifest.describe_update()

    @property
    def can_perform_upgrade(self):
        manifest = self.get_manifest()
        assert manifest is not None
        return manifest.can_perform_upgrade

    def perform_upgrade(self) -> UpgradeResult:
        manifest = self.get_manifest()
        assert manifest is not None
        return manifest.perform_upgrade()

    def describe_post_upgrade(self) -> str:
        manifest = self.get_manifest()
        assert manifest is not None
        return manifest.describe_post_install()
