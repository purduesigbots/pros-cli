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

build_exe_options = {'packages': ['ssl', 'prosconductor.providers.githubreleases'], "include_files": [(requests.certs.where(), 'cacert.pem')]}

modules = []
for pkg in [proscli, prosconductor, prosconductor.providers, prosconfig, prosflasher]:
    modules.append(pkg.__name__)
    # for i, m, p in pkgutil.iter_modules(pkg.__path__):
    #     modules.append('{}.{}'.format(pkg.__name__, m))


if sys.platform == 'win32':
    targetName = 'pros.exe'
else:
    targetName = 'pros'

setup(
    name='purdueros-cli',
    version='2.0',
    packages=modules,
    url='https://github.com/purduesigbots/purdueros-cli',
    license='',
    author='Purdue ACM Sigbots',
    author_email='pros_development@cs.purdue.edu',
    description='',
    options={"build_exe": build_exe_options},
    install_requires=install_reqs,
    executables=[Executable('proscli/main.py', targetName=targetName)]
)

# from esky import bdist_esky
# from setuptools import setup
# from esky.bdist_esky import Executable
# targetName = None
#
# if sys.platform == "win32":
#     targetName = "pros.exe"
#
# setup(
#     name='pros',
#     version='2.0.0',
#     install_requires=[
#         'click',
#         'pyserial',
#         'cx_Freeze',
#         'esky'
#     ],
#     options={'bdist_esky': {
#         'freezer_module': 'cxfreeze',
#         "freezer_options": dict(compress=True)
#     }},
#     scripts=[Executable('proscli/main.py', targetName=targetName)]
# )


# if sys.argv[1] == 'build':
#     from cx_Freeze import setup, Executable
#
#     build_exe_options = {
#         "packages": [
#             "os"
#         ]
#     }
#
#     setup(
#         name='purdueros-cli',
#         version='2.0',
#         packages=['prosflasher', 'proscli'],
#         url='https://github.com/purduesigbots/purdueros-cli',
#         license='',
#         author='Purdue ACM Sigbots',
#         author_email='pros_development@cs.purdue.edu',
#         description='',
#         install_requires=[
#             'click',
#             'pyserial',
#             'cx_Freeze'
#         ],
#         options={"build_exe": build_exe_options},
#         executables=[Executable("proscli/main.py", targetName=targetName)]
#     )
# elif sys.argv[1] == 'bdist_esky':
#     from distutils.core import setup
#     from esky.bdist_esky import bdist_esky, Executable
#     setup(
#         name='purdueros-cli',
#         version='2.0',
#         packages=['prosflasher', 'proscli'],
#         options={
#             "bdist_esky": {
#                 "freezer_module": "cxfreeze",
#                 "compress": "ZIP"
#             }},
#         scripts=[Executable('proscli/main.py')]
#     )
# else:

