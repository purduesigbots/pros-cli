import click
import subprocess
import sys
import os
import prosconfig


@click.group()
def build_cli():
    pass


@build_cli.command()
@click.argument('build-args', nargs=-1)
def make(build_args):
    """Invokes make.

    If on Windows, will invoke make located in on the PROS_TOOLCHAIN.

    Also has the added benefit of looking for the config.pros file"""
    click.echo('Invoking make...')
    cfg = prosconfig.find_project()
    cwd = '.'
    if cfg is not None:
        cwd = cfg.path
    cmd = (os.path.join(os.environ['PROS_TOOLCHAIN'], 'bin', 'make') if os.name == 'nt' else 'make')
    if os.path.exists(cmd):
        subprocess.Popen(executable=cmd, args=build_args, cwd=cwd,
                         stdout=sys.stdout, stderr=sys.stderr)
    else:
        click.echo('Error... make not found.', err=True)
