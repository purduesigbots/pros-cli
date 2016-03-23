from distutils.core import setup


setup(
    name='purdueros-cli',
    version='2.0',
    packages=['prosconductor', 'proscli'],
    url='',
    license='',
    author='Purdue ACM Sigbots',
    author_email='',
    description='',
    install_requires=[
        'click'
    ],
    entry_points="""
        [console_scripts]
        pros-cli=proscli.main:cli
        """
)
