from distutils.core import setup

# setup.py for non-frozen builds
from pip.req import parse_requirements
install_reqs = [str(r.req) for r in parse_requirements('requirements.txt', session=False)]

setup(
    name='pros-cli',
    version='2.beta',
    packages=['prosflasher', 'proscli', 'prosconfig'],
    url='https://github.com/purduesigbots/pros-cli',
    license='',
    author='Purdue ACM Sigbots',
    author_email='pros_development@cs.purdue.edu',
    description='',
    install_requires=install_reqs,
    entry_points="""
        [console_scripts]
        pros=proscli.main:main
        """
)
