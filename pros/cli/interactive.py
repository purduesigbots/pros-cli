from .common import default_options, pros_root, PROSGroup


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
