import click
import subprocess
import sys
import os


@click.group()
def build_cli():
    pass


@build_cli.command()
@click.argument('build-args', nargs=-1)
def build(build_args):
    """Invokes make. If on Windows, will invoke make located in on the PROS_TOOLCHAIN"""
    click.echo('Invoking make...')
    subprocess.run(os.path.join(os.environ['PROS_TOOLCHAIN'], 'bin', 'make') if os.name == 'nt' else
                   'make' + ' ' + ' '.join(build_args),
                   stdout=sys.stdout, stderr=sys.stderr)
