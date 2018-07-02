import os.path
from typing import *

from pros.common.utils import download_file
from .base_instructions import UpgradeInstruction, UpgradeResult


class DownloadInstruction(UpgradeInstruction):
    """
    Downloads a file
    """
    def __init__(self, url='', extension=None, download_description=None, success_explanation=None):
        self.url: str = url
        self.extension: Optional[str] = extension
        self.download_description: Optional[str] = download_description
        self.success_explanation: Optional[str] = success_explanation

    def perform_upgrade(self) -> UpgradeResult:
        assert self.url
        try:
            file = download_file(self.url, ext=self.extension, desc=self.download_description)
            assert file
        except (AssertionError, IOError) as e:
            return UpgradeResult(False, explanation=f'Failed to download required file. ({e})', exception=e)

        if self.success_explanation:
            explanation = self.success_explanation.replace('//FILE\\\\', file) \
                .replace('//SHORT\\\\', os.path.split(file)[1])
        else:
            explanation = f'Downloaded {os.path.split(file)[1]}'
        return UpgradeResult(True, explanation=explanation, file=file, origin=self.url)

    def __str__(self) -> str:
        return 'Download required file.'
