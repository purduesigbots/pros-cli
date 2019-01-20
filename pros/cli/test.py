import time
from pathlib import Path
from typing import *

import click

import pros.common.ui as ui
from pros.common import logger
from pros.conductor import Project
from pros.serial.devices import vex
from pros.serial.ports import DirectPort
from .common import default_options, project_option, pros_root, resolve_v5_port


@pros_root
def test_cli():
    pass


@project_option()
@test_cli.command()
@default_options
def test(project: Project):
    port = resolve_v5_port(None, 'system')
    ser = DirectPort(port)
    device = vex.V5Device(ser)
    # p = Path(r'C:\Users\Elliot\Downloads')
    # output = p.joinpath('firmware.bin')
    # library = p.joinpath('std_library.bin')
    # p = Path(r'C:\Users\Elliot\dev\pros\v5-sdk-beta\sdk\examples\library_demo')
    # output = p.joinpath('build', 'firmware.bin')
    # library = p.joinpath('library', 'build', 'std_library.bin')
    p = project.path
    output = p.joinpath('bin', 'output.package.bin')
    library = p.joinpath('bin', 'v5.package.bin')
    with click.open_file(output, mode='rb') as pf:
        with click.open_file(library, mode='rb') as lf:
            device.write_program(pf, remote_name=project.name, addr=0x07800000,
                                 linked_file=lf, linked_file_addr=0x03800000, linked_remote_name=library.name)