import logging

import click

import pros.cli.build
import pros.cli.terminal
from pros.common.utils import get_version
from .common import default_options


def main():
    try:
        pros_logger = logging.getLogger(pros.__name__)
        pros_logger.propagate = False
        click_handler = logging.StreamHandler()

        formatter = logging.Formatter('%(levelname)s - %(name)s:%(funcName)s - %(message)s')
        click_handler.setFormatter(formatter)
        pros_logger.addHandler(click_handler)
        ctx_obj = {
            'click_handler': click_handler
        }

        cli.main(prog_name='pros', obj=ctx_obj)
    except KeyboardInterrupt:
        click.echo('Aborted!')


def version(ctx: click.Context, param, value):
    if not value:
        return
    ctx.ensure_object(dict)
    if ctx.obj.get('machine_output', False):
        click.echo(get_version())
    else:
        click.echo('pros, version {}'.format(get_version()))
    ctx.exit(0)


@click.command('pros',
               cls=click.CommandCollection,
               sources=[pros.cli.build.build_cli,
                        pros.cli.terminal.terminal_cli])
@default_options
@click.option('--version', help='Displays version and exits', is_flag=True, expose_value=False, is_eager=True,
              callback=version)
def cli():
    pass


if __name__ == '__main__':
    main()
