import os.path

import pros.common.ui as ui
from pros.cli.common import *
from pros.common.cli_config import cli_config


@click.group(cls=PROSGroup)
def misc_commands_cli():
    pass


@misc_commands_cli.command()
@click.option('--force-check', default=False, is_flag=True,
              help='Force check for updates, disregarding auto-check frequency')
@default_options
def upgrade(force_check):
    upgrade_manifest = cli_config().get_upgrade_manifest(force_check)
    if not upgrade_manifest:
        ui.logger(__name__).error('Failed to get upgrade information. Try running with --debug for more information')
    ui.finalize(f'upgrade', upgrade_manifest)


if os.path.exists(os.path.join(__file__, '..', '..', '..', '.git')):
    @misc_commands_cli.command()
    @click.option('--version', default=get_version())
    @click.option('--download-url', prompt=True)
    @click.option('--info-url', prompt=True)
    def create_upgrade_manifest(version, download_url, info_url):
        from pros.common.upgrade import UpgradeManifestV1
        from semantic_version import Version
        import jsonpickle
        upgrade_manifest = UpgradeManifestV1()
        upgrade_manifest.version = Version(version)
        upgrade_manifest.download_url = download_url
        upgrade_manifest.info_url = info_url
        print(jsonpickle.encode(upgrade_manifest))
