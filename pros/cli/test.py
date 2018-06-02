import time

import pros.common.ui as ui
from pros.common import logger

from .click_classes import *
from .common import default_options


@click.group(cls=PROSGroup)
def test_cli():
    pass


@test_cli.command()
@default_options
def test():
    ui.echo('Hello World!')
    with ui.Notification():
        ui.echo('Hello from another box')
    ui.echo('Back on the other one', nl=False)
    ui.echo('Whoops I missed a newline')
    with ui.Notification():
        ui.echo('Yet another box')
        with ui.progressbar(range(20)) as bar:
            for _ in bar:
                time.sleep(0.1)
        ui.echo('more below the ', nl=False)
        ui.echo('progressbar')
    ui.echo('Back in the other notification')

    logger(__name__).warning('Hello')
    try:
        raise Exception('Hey')
    except Exception as e:
        logger(__name__).exception(e)

    ui.finalize('test', {'hello': 'world'}, human_prefix='Created ')

    # ui.confirm('Hey')
