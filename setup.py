# setup.py for non-frozen builds

from setuptools import setup, find_packages
import glob

try:  # for pip >= 10 -- https://stackoverflow.com/a/49867265/3175586
     from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
     from pip.req import parse_requirements


install_reqs = [str(r.req) for r in parse_requirements('requirements.txt', session=False)]

setup(
    name='pros-cli-v5',
    version=open('pip_version').read().strip(),
    packages=find_packages(),
    url='https://github.com/purduesigbots/pros-cli',
    license='MPL-2.0',
    author='Purdue ACM SIGBots',
    author_email='pros_development@cs.purdue.edu',
    description='Command Line Interface for managing PROS projects',
    install_requires=install_reqs,
    entry_points="""
        [console_scripts]
        prosv5=pros.cli.main:main
        """
)
