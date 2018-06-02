from semantic_version import Version

from .utils import get_version


class UpgradeManifestV1(object):
    def __init__(self):
        self.version: Version = None
        self.info_url: str = None
        self.download_url: str = None

    @property
    def needs_upgrade(self):
        return self.version > Version(get_version())

    def __getstate__(self):
        return {
            'needs_upgrade': self.needs_upgrade,
            **self.__dict__
        }

    def describe_upgrade(self):
        if self.needs_upgrade:
            return f'There is an update available! {self.version} is the latest version.\n' \
                   f'Go to {self.info_url} to learn more.\n' \
                   f'Go to {self.download_url} to download.'
        else:
            return f'You are up to date. ({self.version})'

    def __str__(self):
        return self.describe_upgrade()
