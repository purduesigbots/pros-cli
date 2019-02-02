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
    # hot = p.joinpath('firmware.bin')
    # cold = p.joinpath('std_library.bin')
    # p = Path(r'C:\Users\Elliot\dev\pros\v5-sdk-beta\sdk\examples\library_demo')
    # hot = p.joinpath('build', 'firmware.bin')
    # cold = p.joinpath('cold', 'build', 'std_library.bin')
    p = project.path
    hot = p.joinpath('bin', 'hot.package.bin')
    cold = p.joinpath('bin', 'cold.package.bin')
    # with open(hot, mode='rb') as pf:
    #     with open(cold, mode='rb') as lf:
    #         kwargs=dict(target='v5', run_after=device.FTCompleteOptions.DONT_RUN, quirk=0, slot=0, program_version=None, icon=None, ini_config=None, run_screen=True,
    #             remote_name=project.name, addr=project.templates['kernel'].metadata['hot_addr'], force_upload_linked=True,
    #                              linked_file=lf, linked_file_addr=project.templates['kernel'].metadata['cold_addr'], linked_remote_name='1234567890123456789')
    #         print(kwargs)
    #         device.write_program(pf, **kwargs)
    device.ensure_library_space(name='tE57fk9WTMo56tzJi', vid='pros',  target_name=None)
