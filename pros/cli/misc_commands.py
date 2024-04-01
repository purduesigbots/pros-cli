import os
import subprocess

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
@click.argument('configfile', type=click.Path(file_okay=True, dir_okay=False), default=None, required=False)
@default_options
def setup_autocomplete(shell, configfile):
    ui.echo(f"Setting up autocomplete for PROS CLI for {shell} shell in {configfile}...")

    default_configfiles = {
        'bash': '~/.bashrc',
        'zsh': '~/.zshrc',
        'fish': '~/.config/fish/completions/pros.fish'
    }

    if configfile is None:
        configfile = default_configfiles[shell]
    configfile = os.path.expanduser(configfile)

    if shell in ['bash', 'zsh'] and not os.path.exists(configfile):
        raise click.UsageError(f"Config file {configfile} does not exist. Please specify a valid config file.")

    if shell in ['bash', 'zsh']:
        config_dir = os.path.dirname(configfile)
        if not os.path.exists(config_dir):
            raise click.UsageError(f"Config directory {config_dir} does not exist. Please specify a valid config file.")
        script_file = os.path.join(config_dir, f".pros-complete.{shell}")
        with open(script_file, 'w') as f:
            # _PROS_COMPLETE=zsh_source pros > ~/.pros-complete.zsh
            # f.write(os.popen(f"_PROS_COMPLETE={shell}_source pros").read())
            subprocess.Popen(f"_PROS_COMPLETE={shell}_source pros", shell=True, stdout=f).wait()


    # if shell == 'fish':
    #     with open(configfile, 'a') as f:
    #         f.write("\n_PROS_COMPLETE=fish_source pros | source")
