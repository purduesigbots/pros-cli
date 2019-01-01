import click

from pros.common import ui
from .common import default_options, pros_root


@pros_root
def user_script_cli():
    pass


@user_script_cli.command(short_help='Run user script files', hidden=True)
@click.argument('script_file')
@default_options
def user_script(script_file):
    """
    Run a script file with the PROS CLI package
    """
    import os.path
    import importlib.util
    package_name = os.path.splitext(os.path.split(script_file)[0])[0]
    package_path = os.path.abspath(script_file)
    ui.echo(f'Loading {package_name} from {package_path}')
    spec = importlib.util.spec_from_file_location(package_name, package_path)
    spec.loader.load_module()
