import os
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


# Modified from https://github.com/StephLin/click-pwsh/blob/main/click_pwsh/shell_completion.py#L11
_SOURCE_POWERSHELL = r"""Register-ArgumentCompleter -Native -CommandName pros -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $env:COMP_WORDS = $commandAst
    $env:COMP_WORDS = $env:COMP_WORDS.replace('\\', '/')
    $incompleteCommand = $commandAst.ToString()

    $myCursorPosition = $cursorPosition
    if ($myCursorPosition -gt $incompleteCommand.Length) {
        $myCursorPosition = $incompleteCommand.Length
    }
    $env:COMP_CWORD = @($incompleteCommand.substring(0, $myCursorPosition).Split(" ") | Where-Object { $_ -ne "" }).Length
    if ( $wordToComplete.Length -gt 0) { $env:COMP_CWORD -= 1 }

    $env:_PROS_COMPLETE = "powershell_complete"

    pros | ForEach-Object {
        $type, $value, $help = $_.Split(",", 3)
        if ( ($type -eq "plain") -and ![string]::IsNullOrEmpty($value) ) {
            [System.Management.Automation.CompletionResult]::new($value, $value, "ParameterValue", $value)
        }
        elseif ( ($type -eq "file") -or ($type -eq "dir") ) {
            if ([string]::IsNullOrEmpty($wordToComplete)) {
                $dir = "./"
            }
            else {
                $dir = $wordToComplete.replace('\\', '/')
            }
            if ( (Test-Path -Path $dir) -and ((Get-Item $dir) -is [System.IO.DirectoryInfo]) ) {
                [System.Management.Automation.CompletionResult]::new($dir, $dir, "ParameterValue", $dir)
            }
            Get-ChildItem -Path $dir | Resolve-Path -Relative | ForEach-Object {
                $path = $_.ToString().replace('\\', '/').replace('Microsoft.PowerShell.Core/FileSystem::', '')
                $isDir = $false
                if ((Get-Item $path) -is [System.IO.DirectoryInfo]) {
                    $path = $path + "/"
                    $isDir = $true
                }
                if ( ($type -eq "file") -or ( ($type -eq "dir") -and $isDir ) ) {
                    [System.Management.Automation.CompletionResult]::new($path, $path, "ParameterValue", $path)
                }
            }
        }
    }

    $env:COMP_WORDS = $null | Out-Null
    $env:COMP_CWORD = $null | Out-Null
    $env:_PROS_COMPLETE = $null | Out-Null
}
"""


_SOURCE_BASH = r"""_pros_completion() {
    local IFS=$'\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _PROS_COMPLETE=bash_complete $1)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

_pros_completion_setup() {
    complete -o nosort -F _pros_completion pros
}

_pros_completion_setup;
"""


@add_completion_class
class PowerShellComplete(ZshComplete):
    """Shell completion for PowerShell and Windows PowerShell."""

    name = "powershell"
    source_template = _SOURCE_POWERSHELL

    def format_completion(self, item: CompletionItem) -> str:
        return super().format_completion(item).replace("\n", ",")


@misc_commands_cli.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'fish', 'pwsh', 'powershell']), required=True)
@click.argument('config_file', type=click.Path(file_okay=True, dir_okay=False), default=None, required=False)
@click.option('--force', '-f', is_flag=True, default=False, help='Skip confirmation prompts')
@default_options
def setup_autocomplete(shell, config_file, force):
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
        'fish': '~/.config/fish/completions/pros.fish',
        'pwsh': None,
        'powershell': None,
    }

    if shell in ('pwsh', 'powershell') and config_file is None:
        try:
            profile_command = f'{shell} -NoLogo -NoProfile -Command "Write-Output $PROFILE"' if os.name == 'nt' else f"{shell} -NoLogo -NoProfile -Command 'Write-Output $PROFILE'"
            default_config_files[shell] = subprocess.run(profile_command, shell=True, capture_output=True, check=True).stdout.decode().strip()
        except subprocess.CalledProcessError as exc:
            raise click.UsageError("Failed to determine the PowerShell profile path. Please specify a valid config file.") from exc

    if config_file is None:
        config_file = default_config_files[shell]
    config_file = os.path.expanduser(config_file)

    if shell in ('bash', 'zsh'):
        if not os.path.exists(config_file):
            raise click.UsageError(f"Config file {config_file} does not exist. Please specify a valid config file.")

        config_dir = os.path.dirname(config_file)
        if not os.path.exists(config_dir):
            raise click.UsageError(f"Config directory {config_dir} does not exist. Please specify a valid config file.")

        # Write the autocomplete script to a shell script file
        script_file = os.path.join(config_dir, f".pros-complete.{shell}").replace('\\', '/')
        with open(script_file, 'w') as f:
            if os.name == 'nt':
                if shell == "bash":
                    f.write(_SOURCE_BASH)
            else:
                try:
                    subprocess.run(f"_PROS_COMPLETE={shell}_source pros", shell=True, stdout=f, check=True)
                except subprocess.CalledProcessError as exc:
                    raise click.ClickException(f"Failed to write autocomplete script to {script_file}") from exc

        source_autocomplete = f". {script_file}\n"
        if force or ui.confirm(f"Add the autocomplete script to {config_file}?", default=True):
            # Source the autocomplete script in the config file
            with open(config_file, 'r+') as f:
                # Only append if the source command is not already in the file
                if source_autocomplete not in f.readlines():
                    f.write("\n# PROS CLI autocomplete\n")
                    f.write(source_autocomplete)
        else:
            ui.echo(f"Autocomplete script written to {script_file}. Add the following line to {config_file} then restart your shell to enable autocomplete:")
            ui.echo(source_autocomplete)
            return
    elif shell == 'fish':
        config_dir = os.path.dirname(config_file)
        if not os.path.exists(config_dir):
            raise click.UsageError(f"Completions directory {config_dir} does not exist. Please specify a valid completion file.")
        with open(config_file, 'w') as f:
            try:
                subprocess.run(f"_PROS_COMPLETE={shell}_source pros", shell=True, stdout=f, check=True)
            except subprocess.CalledProcessError as exc:
                raise click.ClickException(f"Failed to write autocomplete script to {config_file}") from exc
    elif shell in ('pwsh', 'powershell'):
        if not os.path.exists(config_file):
            raise click.UsageError(f"Config file {config_file} does not exist. Please specify a valid config file.")

        config_dir = os.path.dirname(config_file)
        if not os.path.exists(config_dir):
            raise click.UsageError(f"Config directory {config_dir} does not exist. Please specify a valid config file.")

        # Write the autocomplete script to a PowerShell script file
        script_file = os.path.join(config_dir, "pros-complete.ps1")
        with open(script_file, 'w') as f:
            f.write(_SOURCE_POWERSHELL)

        source_autocomplete = f"{script_file} | Invoke-Expression\n"
        if force or ui.confirm(f"Add the autocomplete script to {config_file}?", default=True):
            # Source the autocomplete script in the config file
            with open(config_file, 'r+') as f:
                # Only append if the source command is not already in the file
                if source_autocomplete not in f.readlines():
                    f.write("\n# PROS CLI autocomplete\n")
                    f.write(source_autocomplete)
        else:
            ui.echo(f"Autocomplete script written to {script_file}. Add the following line to {config_file} then restart your shell to enable autocomplete:")
            ui.echo(source_autocomplete)
            return

    ui.echo(f"Succesfully set up autocomplete for {shell} in {config_file}. Restart your shell to apply changes.")
