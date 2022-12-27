from semantic_version import Version

from pros.common.utils import get_version, logger
from ..instructions import UpgradeResult


class UpgradeManifestV1(object):
    """
    An Upgrade Manifest only capable of determine if there is an update - not how to update
    """

    def __init__(self):
        self.version: Version = None
        self.info_url: str = None

    @property
    def needs_upgrade(self) -> bool:
        """
        :return: True if the current CLI version is less than the upgrade manifest
        """
        return self.version > Version(get_version())

    def describe_update(self) -> str:
        """
        Describes the update
        :return:
        """
        if self.needs_upgrade:
            return f'There is an update available! {self.version} is the latest version.\n' \
                   f'Go to {self.info_url} to learn more.'
        else:
            return f'You are up to date. ({self.version})'

    def __str__(self):
        return self.describe_update()

    @property
    def can_perform_upgrade(self) -> bool:
        return isinstance(self.info_url, str)

    def perform_upgrade(self) -> UpgradeResult:
        logger(__name__).debug(self.__dict__)
        from click import launch
        return UpgradeResult(launch(self.info_url) == 0)

    def describe_post_install(self, **kwargs) -> str:
        return f'Download the latest version from {self.info_url}'
