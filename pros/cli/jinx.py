import asyncio
import json
import queue
from typing import *
import time

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
    jinx_app.start()

    clients: Set[websockets.WebSocketClientProtocol] = set()

    async def client_handler(websocket: websockets.WebSocketClientProtocol, path):
        clients.add(websocket)
        while True:
            await asyncio.sleep(0.005)

    async def jinx_producer():
        while not jinx_app.alive.is_set():
            try:
                data = json.dumps(jinx_app.queue.get(timeout=0.005))
            except queue.Empty:
                continue

            print(data)
            for client in clients:
                try:
                    await client.send(data)
                except:
                    clients.remove(client)
            await asyncio.sleep(.2)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([websockets.serve(client_handler, 'localhost', 9001), jinx_producer()]))
    loop.close()
