from .base_instructions import UpgradeInstruction, UpgradeResult


class NothingInstruction(UpgradeInstruction):
    def __str__(self) -> str:
        return 'No automated instructions. View release notes for installation instructions.'

    def perform_upgrade(self) -> UpgradeResult:
        return UpgradeResult(True)
