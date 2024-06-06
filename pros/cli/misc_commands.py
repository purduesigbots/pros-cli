import os
from pathlib import Path
import subprocess

from click.shell_completion import CompletionItem, add_completion_class, ZshComplete

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


# Script files for each shell
_SCRIPT_FILES = {
    'bash': 'pros-complete.bash',
    'zsh': 'pros-complete.zsh',
    'fish': 'pros.fish',
    'pwsh': 'pros-complete.ps1',
    'powershell': 'pros-complete.ps1',
}


def _get_shell_script(shell: str) -> str:
    """Get the shell script for the specified shell."""
    script_file = Path(__file__).parent.parent / 'autocomplete' / _SCRIPT_FILES[shell]
    with script_file.open('r') as f:
        return f.read()


@add_completion_class
class PowerShellComplete(ZshComplete):  # Identical to ZshComplete except comma delimited instead of newline
    """Shell completion for PowerShell and Windows PowerShell."""

    name = "powershell"
    source_template = _get_shell_script("powershell")

    def format_completion(self, item: CompletionItem) -> str:
        return super().format_completion(item).replace("\n", ",")


@misc_commands_cli.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish', 'pwsh', 'powershell']), required=True)
@click.argument('config_path', type=click.Path(resolve_path=True), default=None, required=False)
@click.option('--force', '-f', is_flag=True, default=False, help='Skip confirmation prompts')
@default_options
def setup_autocomplete(shell, config_path, force):
    """
    Set up autocomplete for PROS CLI

    SHELL: The shell to set up autocomplete for

    CONFIG_PATH: The configuration path to add the autocomplete script to. If not specified, the default configuration
    file for the shell will be used.

    Example: pros setup-autocomplete bash ~/.bashrc
    """

    # https://click.palletsprojects.com/en/8.1.x/shell-completion/

    default_config_paths = {  # Default config paths for each shell
        'bash': '~/.bashrc',
        'zsh': '~/.zshrc',
        'fish': '~/.config/fish/completions/',
        'pwsh': None,
        'powershell': None,
    }

    # Get the powershell profile path if not specified
    if shell in ('pwsh', 'powershell') and config_path is None:
        try:
            profile_command = f'{shell} -NoLogo -NoProfile -Command "Write-Output $PROFILE"' if os.name == 'nt' else f"{shell} -NoLogo -NoProfile -Command 'Write-Output $PROFILE'"
            default_config_paths[shell] = subprocess.run(profile_command, shell=True, capture_output=True, check=True, text=True).stdout.strip()
        except subprocess.CalledProcessError as exc:
            raise click.UsageError("Failed to determine the PowerShell profile path. Please specify a valid config file.") from exc

    # Use default config path if not specified
    if config_path is None:
        config_path = default_config_paths[shell]
        ui.echo(f"Using default config path {config_path}. To specify a different config path, run 'pros setup-autocomplete {shell} [CONFIG_PATH]'.\n")
    config_path = Path(config_path).expanduser().resolve()

    if shell in ('bash', 'zsh', 'pwsh', 'powershell'):
        if config_path.is_dir():
            raise click.UsageError(f"Config file {config_path} is a directory. Please specify a valid config file.")
        if not config_path.exists():
            raise click.UsageError(f"Config file {config_path} does not exist. Please specify a valid config file.")

        # Write the autocomplete script to a shell script file
        script_file = Path(click.get_app_dir("PROS")) / "autocomplete" / _SCRIPT_FILES[shell]
        script_file.parent.mkdir(exist_ok=True)
        with script_file.open('w') as f:
            f.write(_get_shell_script(shell))

        # Source the autocomplete script in the config file
        if shell in ('bash', 'zsh'):
            source_autocomplete = f'. "{script_file.as_posix()}"\n'
        elif shell in ('pwsh', 'powershell'):
            source_autocomplete = f'"{script_file}" | Invoke-Expression\n'
        if force or ui.confirm(f"Add the autocomplete script to {config_path}?", default=True):
            with config_path.open('r+') as f:
                # Only append if the source command is not already in the file
                if source_autocomplete not in f.readlines():
                    f.write("\n# PROS CLI autocomplete\n")
                    f.write(source_autocomplete)
        else:
            ui.echo(f"Autocomplete script written to {script_file}.")
            ui.echo(f"Add the following line to {config_path} then restart your shell to enable autocomplete:\n")
            ui.echo(source_autocomplete)
            return
    elif shell == 'fish':
        # Check if the config path is a directory or file and set the script directory and file accordingly
        if config_path.is_file():
            script_dir = config_path.parent
            script_file = config_path
        else:
            script_dir = config_path
            script_file = config_path / _SCRIPT_FILES[shell]

        if not script_dir.exists():
            raise click.UsageError(f"Completions directory {script_dir} does not exist. Please specify a valid completions file or directory.")

        # Write the autocomplete script to a shell script file
        with script_file.open('w') as f:
            f.write(_get_shell_script(shell))

    ui.echo(f"Succesfully set up autocomplete for {shell} in {config_path}. Restart your shell to apply changes.")
