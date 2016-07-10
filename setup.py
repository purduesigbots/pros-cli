from distutils.core import setup

# setup.py for non-frozen builds

setup(
    name='purdueros-cli',
    version='2.beta',
    packages=['prosflasher', 'proscli', 'prosconfig'],
    url='https://github.com/purduesigbots/purdueros-cli',
    license='',
    author='Purdue ACM Sigbots',
    author_email='pros_development@cs.purdue.edu',
    description='',
    install_requires=[
        'click',
        'pyserial',
        'cachetools',
        'requests',
        'jsonpickle',
        'tabulate'
    ],
    entry_points="""
        [console_scripts]
        pros=proscli.main:main
        """
)
