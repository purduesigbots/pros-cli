import os.path

from click import Context, get_current_context
from pros.common.ui.interactive import parameters, components, application
from pros.conductor import Conductor, Project
from typing import *

T = TypeVar('T')


class ExistingProjectParameter(parameters.ValidatableParameter[str]):
    def update(self, new_value):
        super(ExistingProjectParameter, self).update(Project.find_project(new_value) or new_value)

    def validate(self, value: T):
        project = Project.find_project(value)
        return project is not None or 'Path is not inside a PROS project'


class UpdateProjectModal(application.Modal):

    @property
    def is_processing(self):
        return self._is_processing

    @is_processing.setter
    def is_processing(self, value: bool):
        self._is_processing = bool(value)
        self.redraw()

    def __init__(self, ctx: Optional[Context] = None, conductor: Optional[Conductor] = None):
        super().__init__('Update a project')
        self.conductor = conductor or Conductor()
        self.click_ctx = ctx or get_current_context()
        self._is_processing = True

        self.project: Optional[Project] = None
        self.project_path = ExistingProjectParameter(os.path.join(os.path.expanduser('~'), 'My PROS Project'))

        self.name = parameters.Parameter(None)

        cb = self.project_path.on_changed(self.project_changed, asynchronous=True)
        cb(self.project_path)

    def project_changed(self, new_project: ExistingProjectParameter):
        self.is_processing = True
        self.project = Project(new_project.value)

        self.name.update(self.project.project_name)

        self.is_processing = False

    def confirm(self, *args, **kwargs):
        pass

    def build(self) -> Generator[components.Component, None, None]:
        yield components.DirectorySelector('Project Directory', self.project_path)
        if self.is_processing:
            yield components.Spinner()
        else:
            assert self.project is not None
            yield components.Label(f'Modify your {self.project.target} project.')
            yield components.InputBox('Project Name', self.name)
