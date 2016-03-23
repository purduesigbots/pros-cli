import click
import proscli


@click.command(name='pros',
               cls=click.CommandCollection,
               sources=[proscli.conductor_cli, proscli.terminal_cli, proscli.build_cli])
@click.version_option(version='2.0.beta')
def cli():
    pass


if __name__ == '__main__':
    cli()
