import click
#from pkg_resources import get_distribution
import proscli
from proscli.utils import default_options, get_version

def main():
    # the program name should always be pros. don't care if it's not...
    try:
        cli.main(prog_name='pros')
    except KeyboardInterrupt:
        click.echo('Aborted!')

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
