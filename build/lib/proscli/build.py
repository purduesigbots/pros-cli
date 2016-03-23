import click
import subprocess
import sys


@click.group()
def build_cli():
    pass


@build_cli.command()
def build():
    subprocess.run('make', stdout=sys.stdout, stderr=sys.stderr)
