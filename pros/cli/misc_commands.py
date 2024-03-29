import pros.common.ui as ui
from pros.cli.common import *
from pros.ga.analytics import analytics

@pros_root
def misc_commands_cli():
    pass


@misc_commands_cli.command()
@click.option('--force-check', default=False, is_flag=True,
              help='Force check for updates, disregarding auto-check frequency')
@click.option('--no-install', default=False, is_flag=True,
              help='Only check if a new version is available, do not attempt to install')
@default_options
def upgrade(force_check, no_install):
    """
    Check for updates to the PROS CLI
    """
    with ui.Notification():
        ui.echo('The "pros upgrade" command is currently non-functioning. Did you mean to run "pros c upgrade"?', color='yellow')
        
    return # Dead code below
    
    analytics.send("upgrade")
    from pros.upgrade import UpgradeManager
    manager = UpgradeManager()
    manifest = manager.get_manifest(force_check)
    ui.logger(__name__).debug(repr(manifest))
    if manager.has_stale_manifest:
        ui.logger(__name__).error('Failed to get latest upgrade information. '
                                  'Try running with --debug for more information')
        return -1
    if not manager.needs_upgrade:
        ui.finalize('upgradeInfo', 'PROS CLI is up to date')
    else:
        ui.finalize('upgradeInfo', manifest)
        if not no_install:
            if not manager.can_perform_upgrade:
                ui.logger(__name__).error(f'This manifest cannot perform the upgrade.')
                return -3
            ui.finalize('upgradeComplete', manager.perform_upgrade())


@misc_commands_cli.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish']), required=True)
@click.argument('rcfile', type=click.Path(file_okay=True, dir_okay=False), required=True)
@default_options
def setup_autocomplete(shell, rcfile):
    ui.echo(f"Setting up autocomplete for PROS CLI for {shell} shell in {rcfile}...")

    if shell == 'bash':
        with open(rcfile, 'a') as f:
            f.write('\neval "$(_PROS_COMPLETE=bash_source pros)"')

    if shell == 'zsh':
        with open(rcfile, 'a') as f:
            f.write('\neval "$(_PROS_COMPLETE=zsh_source pros)"')

    if shell == 'fish':
        with open(rcfile, 'a') as f:
            f.write("\n_PROS_COMPLETE=fish_source pros | source")
