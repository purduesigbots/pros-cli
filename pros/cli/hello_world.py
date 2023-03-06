from .common import default_options, pros_root
import click

@pros_root
def hello_world_cli():
    pass

@hello_world_cli.command()
@click.option("--name")
def hello_world(name):
    print(f"Hello {name}, my name is craig")