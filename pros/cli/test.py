import time

from pros.cli.common import resolve_v5_port
from pros.jinx import JinxApplication
from pros.serial.devices.vex import V5UserDevice
from pros.serial.ports import DirectPort
from .click_classes import *
from .common import default_options


@click.group(cls=PROSGroup)
def test_cli():
    pass


@test_cli.command()
@default_options
def test():
    jinx = JinxApplication(V5UserDevice(DirectPort(resolve_v5_port(None, 'user'))))
    jinx.start()
    while not jinx.alive.is_set():
        time.sleep(0.005)
        try:
            data = jinx.queue.get(timeout=0.005)
            print(data)
        except:
            pass
    jinx.join()
    # ui.echo('Hello World!')
    # with ui.Notification():
    #     ui.echo('Hello from another box')
    # ui.echo('Back on the other one', nl=False)
    # ui.echo('Whoops I missed a newline')
    # with ui.Notification():
    #     ui.echo('Yet another box')
    #     with ui.progressbar(range(20)) as bar:
    #         for _ in bar:
    #             time.sleep(0.1)
    #     ui.echo('more below the ', nl=False)
    #     ui.echo('progressbar')
    # ui.echo('Back in the other notification')
    #
    # logger(__name__).warning('Hello')
    # try:
    #     raise Exception('Hey')
    # except Exception as e:
    #     logger(__name__).exception(e)
    #
    # ui.finalize('test', {'hello': 'world'}, human_prefix='Created ')
    #
    # # ui.confirm('Hey')
