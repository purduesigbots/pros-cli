from .common import PROSGroup, default_options, pros_root


@pros_root
def interactive_cli():
    pass


@interactive_cli.group(cls=PROSGroup, hidden=True)
@default_options
def interactive():
    pass


@interactive.command()
@default_options
def new_project():
    from pros.common.ui.interactive.renderers import MachineOutputRenderer
    from pros.conductor.interactive.NewProjectModal import NewProjectModal
    app = NewProjectModal()
    MachineOutputRenderer(app).run()


@interactive.command()
@default_options
def update_project():
    from pros.common.ui.interactive.renderers import MachineOutputRenderer
    from pros.conductor.interactive.UpdateProjectModal import UpdateProjectModal
    app = UpdateProjectModal()
    MachineOutputRenderer(app).run()


@interactive.command()
@default_options
def upload():
    from pros.common.ui.interactive.renderers import MachineOutputRenderer
    from pros.serial.interactive import UploadProjectModal
    MachineOutputRenderer(UploadProjectModal()).run()
