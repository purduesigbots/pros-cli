import sys
import esky
import click
import proscli
from proscli.utils import default_options


def main():
    # the program name should always be pros. don't care if it's not...
    cli.main(prog_name='pros')


@click.command('pros',
               cls=click.CommandCollection,
               context_settings=dict(help_option_names=['-h', '--help']),
               sources=[proscli.conductor_cli, proscli.terminal_cli, proscli.build_cli, proscli.flasher_cli])
@click.version_option(version='2.0.0', prog_name='pros')
@default_options
def cli():
    pass


if __name__ == '__main__':
    main()
