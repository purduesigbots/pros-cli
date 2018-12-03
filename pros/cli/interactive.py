from typing import *

import pros.conductor as c
from .common import PROSGroup, default_options, project_option, pros_root


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
@project_option(required=False)
@default_options
def update_project(project: Optional[c.Project]):
    from pros.common.ui.interactive.renderers import MachineOutputRenderer
    from pros.conductor.interactive.UpdateProjectModal import UpdateProjectModal
    app = UpdateProjectModal(project)
    MachineOutputRenderer(app).run()


@interactive.command()
@project_option(required=False)
@default_options
def upload(project: Optional[c.Project]):
    from pros.common.ui.interactive.renderers import MachineOutputRenderer
    from pros.serial.interactive import UploadProjectModal
    MachineOutputRenderer(UploadProjectModal(project)).run()
