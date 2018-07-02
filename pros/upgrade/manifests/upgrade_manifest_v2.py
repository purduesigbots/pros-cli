import sys
from enum import Enum
from typing import *

from pros.common import logger
from .upgrade_manifest_v1 import UpgradeManifestV1
from ..instructions import UpgradeInstruction, UpgradeResult, NothingInstruction


class PlatformsV2(Enum):
    Unknown = 0
    Windows86 = 1
    Windows64 = 2
    MacOS = 3
    Linux = 4
    Pip = 5


class UpgradeManifestV2(UpgradeManifestV1):
    """
    an Upgrade Manifest capable of determining if there is an update, and possibly an installer to download,
    but without the knowledge of how to run the installer
    """

    def __init__(self):
        super().__init__()
        self.platform_instructions: Dict[PlatformsV2, UpgradeInstruction] = {}

        self._platform: 'PlatformsV2' = None

        self._last_file: Optional[str] = None

    @property
    def platform(self) -> 'PlatformsV2':
        """
        Attempts to detect the current platform type
        :return: The detected platform type, or Unknown
        """
        if self._platform is not None:
            return self._platform
        if getattr(sys, 'frozen', False):
            import BUILD_CONSTANTS
            frozen_platform = getattr(BUILD_CONSTANTS, 'FROZEN_PLATFORM_V1', None)
            if isinstance(frozen_platform, str):
                if frozen_platform.startswith('Windows86'):
                    self._platform = PlatformsV2.Windows86
                elif frozen_platform.startswith('Windows64'):
                    self._platform = PlatformsV2.Windows64
                elif frozen_platform.startswith('MacOS'):
                    self._platform = PlatformsV2.MacOS
        else:
            try:
                from pip._vendor import pkg_resources
                results = [p for p in pkg_resources.working_set if p.project_name.startswith('pros-cli')]
                if any(results):
                    self._platform = PlatformsV2.Pip
            except ImportError:
                pass
        if not self._platform:
            self._platform = PlatformsV2.Unknown
        return self._platform

    @property
    def can_perform_upgrade(self) -> bool:
        return True

    def perform_upgrade(self) -> UpgradeResult:
        instructions: UpgradeInstruction = self.platform_instructions.get(self.platform, NothingInstruction())
        logger(__name__).debug(self.__dict__)
        logger(__name__).debug(f'Platform: {self.platform}')
        logger(__name__).debug(instructions.__dict__)
        return instructions.perform_upgrade()

    def __repr__(self):
        return repr({
            'platform': self.platform,
            **self.__dict__
        })
