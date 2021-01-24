import os
import sys
from distutils.util import get_platform

import requests.certs
from cx_Freeze import Executable, setup
from install_requires import install_requires as install_reqs

import pros.cli.main

build_exe_options = {
    'packages': ['ssl', 'requests', 'idna'] + [f'pros.cli.{root_source}' for root_source in pros.cli.main.root_sources],
    "include_files": [(requests.certs.where(), 'cacert.pem')],
    'excludes': ['pip', 'distutils'],  # optimization excludes
    'constants': [
        f'{key}=\'{value}\'' for key, value in {
            'CLI_VERSION': open('version').read().strip(),
            'FROZEN_PLATFORM_V1': 'Windows64' if get_platform() == 'win-amd64' else 'Windows86'
        }.items()
    ],
    'include_msvcr': True
    # 'zip_include_packages': [],
    # 'zip_exclude_packages': []
}

build_mac_options = {
    'bundle_name': 'PROS CLI',
    'iconfile': 'pros.icns'
}

if os.environ.get('MAC_SIGNING_IDENTITY') is not None:
    build_mac_options['codesign_identity'] = os.environ.get('MAC_SIGNING_IDENTITY')
    build_mac_options['codesign_deep'] = True

modules = ['pros']

if sys.platform == 'win32':
    extension = '.exe'
else:
    extension = ''

setup(
    name='pros-cli',
    version=open('pip_version').read().strip(),
    packages=modules,
    url='https://github.com/purduesigbots/pros-cli',
    license='MPL-2.0',
    author='Purdue ACM Sigbots',
    author_email='pros_development@cs.purdue.edu',
    description='Command Line Interface for managing PROS projects',
    options={"build_exe": build_exe_options, 'bdist_mac': build_mac_options},
    install_requires=install_reqs,
    executables=[Executable('pros/cli/main.py', target_name=f'pros{extension}'),
                 Executable('pros/cli/main.py', target_name=f'prosv5{extension}'),
                 Executable('pros/cli/compile_commands/intercept-cc.py', target_name=f'intercept-cc{extension}'),
                 Executable('pros/cli/compile_commands/intercept-cc.py', target_name=f'intercept-c++{extension}')]
)

if sys.argv[1] == 'build_exe':
    import distutils.util

    build_dir = './build/exe.{}-{}.{}'.format(distutils.util.get_platform(), sys.version_info[0], sys.version_info[1])
    import shutil
    import platform

    shutil.make_archive('pros_cli-{}-{}-{}'.format(open('version').read().strip(), platform.system()[0:3].lower(),
                                                   platform.architecture()[0]), 'zip', build_dir, '.')
