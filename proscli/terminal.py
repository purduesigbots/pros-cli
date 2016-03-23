import click


@click.group()
def terminal_cli():
    pass


@terminal_cli.command()
def terminal():
    click.echo('hello terminal')
