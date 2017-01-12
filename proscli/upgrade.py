import click
from proscli.utils import default_cfg
import os
import os.path
import subprocess
import sys

import json

@click.group()
def upgrade_cli():
    pass


def get_upgrade_command():
    if getattr(sys, 'frozen', False):
        cmd = os.path.abspath(os.path.join(sys.executable, '..', '..', 'updater.exe'))
        if os.path.exists(cmd):
            return [cmd, '/silentall', '-nofreqcheck']
        else:
            return False
    else:
        try:
            from pip._vendor import pkg_resources
            results = [p for p in pkg_resources.working_set if p.project_name == 'pros-cli']
            if os.path.exists(os.path.join(results[0].location, '.git')):
                if subprocess.run('where git').returncode == 0:
                    return ['git', 'pull']
                elif subprocess.run('where bash').returncode == 0:
                    return ['bash', '-c', 'git pull']
                else:
                    return False
            if len(results) == 0 or not hasattr(results[0], 'location'):
                return False
            else:
                return ['pip', 'install', '-U', '-t', results[0].location, 'pros-cli']
        except Exception:
            return False


@upgrade_cli.command('upgrade', help='Provides a facility to run upgrade the PROS CLI')
@default_cfg
def upgrade(cfg):
    cmd = get_upgrade_command()
    if cmd is False:
        click.echo('Could not determine installation type.')
        sys.exit(1)
        return
    elif not cfg.machine_output:
        sys.exit(subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode
    else:
        for piece in cmd:
            click.echo(piece)
