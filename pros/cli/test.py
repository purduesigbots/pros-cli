import click
from .common import *


@click.group()
def test_cli():
    pass


@test_cli.command()
@default_options
def test():
    print('')
    click.secho('Hello', color='yellow')
