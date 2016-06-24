import click
import proscli


@click.command(name='pros',
               cls=click.CommandCollection,
               context_settings=dict(help_option_names=['-h', '--help']),
               sources=[proscli.conductor_cli, proscli.terminal_cli, proscli.build_cli, proscli.flasher_cli])
@click.version_option(version='2.0.beta')
def cli():
    pass


if __name__ == '__main__':
    cli()
