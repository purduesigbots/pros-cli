# setup.py for non-frozen builds

from setuptools import setup, find_packages
from install_requires import install_requires as install_reqs

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
