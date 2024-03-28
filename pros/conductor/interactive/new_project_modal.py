import os.path
from typing import *

from click import Context, get_current_context

from pros.common import ui
from pros.common.ui.interactive import application, components, parameters
from pros.conductor import Conductor
from .parameters import NonExistentProjectParameter


class NewProjectModal(application.Modal[None]):
    targets = parameters.OptionParameter('v5', ['v5', 'cortex'])
    kernel_versions = parameters.OptionParameter('latest', ['latest'])
    install_default_libraries = parameters.BooleanParameter(True)

    project_name = parameters.Parameter(None)
    advanced_collapsed = parameters.BooleanParameter(True)

    def __init__(self, ctx: Context = None, conductor: Optional[Conductor] = None,
                 directory=os.path.join(os.path.expanduser('~'), 'My PROS Project')):
        super().__init__('Create a new project')
        self.conductor = conductor or Conductor()
        self.click_ctx = ctx or get_current_context()
        self.directory = NonExistentProjectParameter(directory)

        cb = self.targets.on_changed(self.target_changed, asynchronous=True)
        cb(self.targets)

    def target_changed(self, new_target):
        templates = self.conductor.resolve_templates('kernel', target=new_target.value)
        if len(templates) == 0:
            self.kernel_versions.options = ['latest']
        else:
            self.kernel_versions.options = ['latest'] + sorted({t.version for t in templates}, reverse=True)
        self.redraw()

    def confirm(self, *args, **kwargs):
        assert self.can_confirm
        self.exit()
        project = self.conductor.new_project(
            path=self.directory.value,
            target=self.targets.value,
            version=self.kernel_versions.value,
            no_default_libs=not self.install_default_libraries.value,
            project_name=self.project_name.value
        )

        from pros.conductor.project import ProjectReport
        report = ProjectReport(project)
        ui.finalize('project-report', report)

        with ui.Notification():
            ui.echo('Building project...')
            project.compile([])

    @property
    def can_confirm(self):
        return self.directory.is_valid() and self.targets.is_valid() and self.kernel_versions.is_valid()

    def build(self) -> Generator[components.Component, None, None]:
        yield components.DirectorySelector('Project Directory', self.directory)
        yield components.ButtonGroup('Target', self.targets)

        project_name_placeholder = os.path.basename(os.path.normpath(os.path.abspath(self.directory.value)))

        yield components.Container(
            components.InputBox('Project Name', self.project_name, placeholder=project_name_placeholder),
            components.DropDownBox('Kernel Version', self.kernel_versions),
            components.Checkbox('Install default libraries', self.install_default_libraries),
            title='Advanced',
            collapsed=self.advanced_collapsed
        )
