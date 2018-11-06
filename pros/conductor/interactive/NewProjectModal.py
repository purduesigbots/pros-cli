import os.path
import sys

from click import Context, get_current_context
from pros.common import ui
from pros.common.ui.interactive import parameters, components, application
from pros.common.ui.interactive.parameters.validatable_parameter import T
from pros.conductor import Conductor, Project
from typing import *


class NonExistentProjectParameter(parameters.ValidatableParameter[str]):
    def validate(self, value: T) -> Union[bool, str]:
        value = os.path.abspath(value)
        if os.path.isfile(value):
            return 'Path is a file'
        if os.path.isdir(value) and not os.access(value, os.W_OK):
            return 'Do not have write permission to path'
        if Project.find_project(value) is not None:
            return 'Project path already exists, delete it first'
        blacklisted_directories = []
        # TODO: Proper Windows support
        if sys.platform == 'win32':
            blacklisted_directories.extend([
                os.environ.get('WINDIR', os.path.join('C:', 'Windows')),
                os.environ.get('PROGRAMFILES', os.path.join('C:', 'Program Files'))
            ])
        if any(value.startswith(d) for d in blacklisted_directories):
            return 'Cannot create project in a system directory'
        if not os.path.exists(value):
            parent = os.path.split(value)[0]
            while parent and not os.path.exists(parent):
                temp_value = os.path.split(parent)[0]
                if parent == temp_value:
                    break
                parent = temp_value
            if not parent:
                return 'Cannot create directory because root does not exist'
            if not os.path.exists(parent):
                return f'Cannot create directory because {parent} does not exist'
            if not os.path.isdir(parent):
                return f'Cannot create directory because {parent} is a file'
            if not os.access(parent, os.W_OK | os.X_OK):
                return f'Cannot create directory because missing write permissions to {parent}'
        return True


class NewProjectModal(application.Modal):
    directory = NonExistentProjectParameter(os.path.join(os.path.expanduser('~'), 'My PROS Project'))
    targets = parameters.OptionParameter('v5', ['v5', 'cortex'])
    kernel_versions = parameters.OptionParameter('latest', ['latest'])
    install_default_libraries = parameters.BooleanParameter(True)

    project_name = parameters.Parameter(None)
    advanced_collapsed = parameters.BooleanParameter(True)

    def __init__(self, ctx: Context = None, conductor: Optional[Conductor] = None):
        super().__init__('Create a new project')
        self.conductor = conductor or Conductor()
        self.click_ctx = ctx or get_current_context()

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
