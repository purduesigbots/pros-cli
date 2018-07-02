from .base_instructions import UpgradeResult
from .download_instructions import DownloadInstruction


class ExplorerInstruction(DownloadInstruction):
    """
    Opens file explorer of the downloaded file
    """

    def perform_upgrade(self) -> UpgradeResult:
        result = super().perform_upgrade()
        if result.successful:
            import click
            click.launch(getattr(result, 'file'))
        return result

    def __str__(self) -> str:
        return 'Download required file.'
