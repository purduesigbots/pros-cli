from pros.common.ui.interactive.renderers import MachineOutputRenderer
from pros.conductor.interactive.NewProjectModal import NewProjectModal

from .common import default_options, pros_root


@pros_root
def test_cli():
    pass


@test_cli.command()
@default_options
def test():
    app = NewProjectModal()
    MachineOutputRenderer(app).run()

    # ui.confirm('Hey')
