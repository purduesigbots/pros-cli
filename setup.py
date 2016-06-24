from distutils.core import setup


setup(
    name='purdueros-cli',
    version='2.0',
    packages=['prosconductor', 'proscli'],
    url='https://github.com/purduesigbots/purdueros-cli',
    license='',
    author='Purdue ACM Sigbots',
    author_email='pros_development@cs.purdue.edu',
    description='',
    install_requires=[
        'click',
        'pyserial'
    ],
    entry_points="""
        [console_scripts]
        pros=proscli.main:cli
        """
)
