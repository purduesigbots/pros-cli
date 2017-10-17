import sys
from cx_Freeze import Executable, setup
import pkgutil
from pip.req import parse_requirements
import requests.certs

import proscli
import prosconductor
import prosconductor.providers
import prosconfig
import prosflasher

install_reqs = [str(r.req) for r in parse_requirements('requirements.txt', session=False)]

build_exe_options = {
    'packages': ['ssl', 'prosconductor.providers.githubreleases', 'requests', 'idna'],
    "include_files": [(requests.certs.where(), 'cacert.pem')],
    'excludes': ['pip', 'distutils'], # optimization excludes
    'constants': ['CLI_VERSION=\'{}\''.format(open('version').read().strip())],
    'include_msvcr': True
    # 'zip_include_packages': [],
    # 'zip_exclude_packages': []
}

build_mac_options = {
    'bundle_name': 'PROS CLI',
    'iconfile': 'pros.icns'
}

modules = []
for pkg in [proscli, prosconductor, prosconductor.providers, prosconfig, prosflasher]:
    modules.append(pkg.__name__)


if sys.platform == 'win32':
    targetName = 'pros.exe'
else:
    targetName = 'pros'

setup(
    name='pros-cli-v5',
    version=open('pip_version').read().strip(),
    packages=modules,
    url='https://github.com/purduesigbots/pros-cli',
    license='MPL-2.0',
    author='Purdue ACM Sigbots',
    author_email='pros_development@cs.purdue.edu',
    description='Command Line Interface for managing PROS projects',
    options={"build_exe": build_exe_options, 'bdist_mac': build_mac_options},
    install_requires=install_reqs,
    executables=[Executable('proscli/main.py', targetName=targetName)]
)

if sys.argv[1] == 'build_exe':
    import py_compile
    import distutils.util
    build_dir='./build/exe.{}-{}.{}'.format(distutils.util.get_platform(),sys.version_info[0],sys.version_info[1])
    py_compile.compile('./prosconductor/providers/githubreleases.py', cfile='{}/githubreleases.pyc'.format(build_dir))
    import shutil
    import platform
    shutil.make_archive('pros_cli-{}-{}-{}'.format(open('version').read().strip(), platform.system()[0:3].lower(), platform.architecture()[0]), 'zip', build_dir, '.')
