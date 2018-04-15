import asyncio
import json

import click
import websockets

from pros.cli.common import resolve_v5_port
from pros.jinx import JinxApplication
from pros.serial.devices.vex import V5UserDevice
from pros.serial.ports import DirectPort
from .common import PROSGroup, default_options


def convert(b: str) -> str:
    return ''.join(reversed([b[i:i + 2] for i in range(0, len(b), 2)]))


@click.group(cls=PROSGroup)
def jinx_cli():
    pass


async def producer_handler(websocket: websockets.WebSocketClientProtocol, path, jioknx_app: JinxApplication):
    while True:
        await websocket.send(json.dumps(jinx_app.queue.get()))


@jinx_cli.command(short_help='Run JINX, the graphical debugger for PROS')
@default_options
def jinx():
    """
    JINX is PROS's graphical debugger. This command runs the JINX webserver

    Visit https://pros.cs.purdue.edu/v5/cli/jinx to learn more
    """
    port = DirectPort(resolve_v5_port(None, 'user'))
    device = V5UserDevice(port)
    jinx_app = JinxApplication(device)
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(producer_handler, 'localhost', 9001, jinx_app=jinx_app)
    loop.run_until_complete(start_server)
    loop.run_forever()
    click.echo('after server')
