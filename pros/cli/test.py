from pros.common.ui.interactive.renderer import MachineOutputRenderer
from pros.conductor.interactive.NewProjectModal import NewProjectModal
from pros.serial.terminal.console import Console
from .common import default_options, pros_root


@pros_root
def test_cli():
    pass


@test_cli.command()
@default_options
def test():
    app = NewProjectModal()
    MachineOutputRenderer().run(app)

    # ui.confirm('Hey')
