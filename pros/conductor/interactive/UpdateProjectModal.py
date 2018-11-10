import os.path

from click import Context, get_current_context
from typing import *

from pros.common import ui
from pros.common.ui.interactive import parameters, components, application
from pros.conductor import Conductor, Project, BaseTemplate
from .parameters import ExistingProjectParameter


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
        self._is_processing = False

        self.project: Optional[Project] = None
        self.project_path = ExistingProjectParameter(os.path.join(os.path.expanduser('~'), 'My PROS Project'))

        self.name = parameters.Parameter(None)
        self.kernel_versions = parameters.OptionParameter('latest', ['latest'])
        self.template_versions: Dict[str, parameters.OptionParameter] = dict()

        self.templates_collapsed = parameters.BooleanParameter(False)

        cb = self.project_path.on_changed(self.project_changed, asynchronous=True)
        if self.project_path.is_valid():
            cb(self.project_path)

    def project_changed(self, new_project: ExistingProjectParameter):
        try:
            self.is_processing = True
            self.project = Project(new_project.value)

            self.name.update(self.project.project_name)

            kernel_templates = self.conductor.resolve_templates('kernel', target=self.project.target)
            if len(kernel_templates) == 0:
                self.kernel_versions.options = ['latest']
            else:
                self.kernel_versions.options = ['latest'] + sorted({t.version for t in kernel_templates}, reverse=True)

            self.template_versions: Dict[str, parameters.OptionParameter] = dict()
            for template in self.project.templates.keys():
                if template == 'kernel':
                    continue
                template_query = BaseTemplate(name=template, version='>=0')
                candidate_templates = self.conductor.resolve_templates(template_query)
                self.template_versions[template_query.name] = parameters.OptionParameter(
                    'latest',
                    ['latest', 'uninstall'] + sorted({t.version for t in candidate_templates}, reverse=True)
                )

            self.is_processing = False
        except BaseException as e:
            ui.logger(__name__).exception(e)

    def confirm(self, *args, **kwargs):
        pass

    def build(self) -> Generator[components.Component, None, None]:
        yield components.DirectorySelector('Project Directory', self.project_path)
        if self.is_processing:
            yield components.Spinner()
        elif self.project_path.is_valid():
            assert self.project is not None
            yield components.Label(f'Modify your {self.project.target} project.')
            yield components.InputBox('Project Name', self.name)
            yield components.DropDownBox('Kernel Version', self.kernel_versions)
            templates = [
                components.DropDownBox(name, parameter)
                for name, parameter
                in self.template_versions.items()
            ]
            yield components.Container(
                *templates,
                title='Templates',
                collapsed=self.templates_collapsed
            )
