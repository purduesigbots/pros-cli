import sys
from enum import Enum
from typing import *

from pros.common import logger
from .upgrade_manifest_v1 import UpgradeManifestV1
from ..instructions import UpgradeInstruction, UpgradeResult, NothingInstruction


class PlatformsV2(Enum):
    UNKNOWN = 0
    WINDOWS86 = 1
    WINDOWS64 = 2
    MACOS = 3
    LINUX = 4
    PIP = 5


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
        :return: The detected platform type, or UNKNOWN
        """
        if self._platform is not None:
            return self._platform
        if getattr(sys, 'frozen', False):
            import _constants
            frozen_platform = getattr(_constants, 'FROZEN_PLATFORM_V1', None)
            if isinstance(frozen_platform, str):
                if frozen_platform.startswith('Windows86'):
                    self._platform = PlatformsV2.WINDOWS86
                elif frozen_platform.startswith('Windows64'):
                    self._platform = PlatformsV2.WINDOWS64
                elif frozen_platform.startswith('MacOS'):
                    self._platform = PlatformsV2.MACOS
        else:
            try:
                from pip._vendor import pkg_resources
                # pylint: disable=not-an-iterable
                results = [p for p in pkg_resources.working_set if p.project_name.startswith('pros-cli')]
                if any(results):
                    self._platform = PlatformsV2.PIP
            except ImportError:
                pass
        if not self._platform:
            self._platform = PlatformsV2.UNKNOWN
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
