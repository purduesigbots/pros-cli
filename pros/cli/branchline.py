from pros.cli.common import *
from pros.common import ui
from .conductor import conductor

@conductor.group(aliases=["b", "branch"], short_help="Manage branchline templates")
@default_options
def branchline():
    pass

@branchline.command("list", help="List available branchline templates")
def list_branchline():
    ui.echo("Branchline templates:")
    