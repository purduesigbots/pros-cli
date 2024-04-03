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
@click.argument('config_file', type=click.Path(file_okay=True, dir_okay=False), default=None, required=False)
@default_options
def setup_autocomplete(shell, config_file):
    """
    Set up autocomplete for PROS CLI in the specified shell

    SHELL: The shell to set up autocomplete for

    CONFIG_FILE: The configuration file to add the autocomplete script to. If not specified, the default configuration
    file for the shell will be used.
    """

    # https://click.palletsprojects.com/en/8.1.x/shell-completion/

    default_config_files = {
        'bash': '~/.bashrc',
        'zsh': '~/.zshrc',
        'fish': '~/.config/fish/completions/pros.fish'
    }

    if config_file is None:
        config_file = default_config_files[shell]
    config_file = os.path.expanduser(config_file)

    if shell in ['bash', 'zsh']:
        if not os.path.exists(config_file):
            raise click.UsageError(f"Config file {config_file} does not exist. Please specify a valid config file.")

        config_dir = os.path.dirname(config_file)
        if not os.path.exists(config_dir):
            raise click.UsageError(f"Config directory {config_dir} does not exist. Please specify a valid config file.")

        # Write the autocomplete script to a shell script file
        script_file = os.path.join(config_dir, f".pros-complete.{shell}")
        with open(script_file, 'w') as f:
            try:
                subprocess.run(f"_PROS_COMPLETE={shell}_source pros", shell=True, stdout=f, check=True)
            except subprocess.CalledProcessError as exc:
                raise click.ClickException(f"Failed to write autocomplete script to {script_file}") from exc

        # Source the autocomplete script in the config file
        source_autocomplete = f". ~/.pros-complete.{shell}\n"
        with open(config_file, 'r+') as f:
            # Only append if the source command is not already in the file
            if source_autocomplete not in f.readlines():
                f.write("\n# PROS CLI autocomplete\n")
                f.write(source_autocomplete)
    elif shell == 'fish':
        config_dir = os.path.dirname(config_file)
        if not os.path.exists(config_dir):
            raise click.UsageError(f"Config directory {config_dir} does not exist. Please specify a valid config file.")
        with open(config_file, 'w') as f:
            try:
                subprocess.run(f"_PROS_COMPLETE={shell}_source pros", shell=True, stdout=f, check=True)
            except subprocess.CalledProcessError as exc:
                raise click.ClickException(f"Failed to write autocomplete script to {config_file}") from exc

    ui.echo(f"Succesfully set up autocomplete for PROS CLI for {shell} in {config_file}. Restart your shell to apply changes.")
