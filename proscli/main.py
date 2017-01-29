import click
#from pkg_resources import get_distribution
import proscli
from proscli.utils import default_options
import os.path
import sys


def main():
    # the program name should always be pros. don't care if it's not...
    try:
        cli.main(prog_name='pros')
    except KeyboardInterrupt:
        click.echo('Aborted!')


def get_version():
    try:
        if os.path.isfile(os.path.join(__file__, '../../version')):
            return open(os.path.join(__file__, '../../version')).read().strip()
    except Exception:
        pass
    try:
        if getattr(sys, 'frozen', False):
            import BUILD_CONSTANTS
            return BUILD_CONSTANTS.CLI_VERSION
    except Exception:
        pass
    return None # Let click figure it out


@click.command('pros',
               cls=click.CommandCollection,
               context_settings=dict(help_option_names=['-h', '--help']),
               sources=[proscli.terminal_cli, proscli.build_cli, proscli.flasher_cli,
                        proscli.conductor_cli, proscli.upgrade_cli])
@click.version_option(version=get_version(), prog_name='pros')
@default_options
def cli():
    pass


if __name__ == '__main__':
    main()
