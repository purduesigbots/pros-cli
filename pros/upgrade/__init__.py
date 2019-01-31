from .upgrade_manager import UpgradeManager, UpgradeManifestV2


def get_platformv2():
    return UpgradeManifestV2().platform


__all__ = ['UpgradeManager', 'get_platformv2']
