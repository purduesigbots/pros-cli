import os.path
from typing import *

from click import Context, get_current_context
from semantic_version import Version

from pros.common import ui
from pros.common.ui.interactive import application, components, parameters
from pros.conductor import BaseTemplate, Conductor, Project
from pros.conductor.project.ProjectTransaction import ProjectTransaction
from .components import TemplateListingComponent
from .parameters import ExistingProjectParameter, TemplateParameter


class UpdateProjectModal(application.Modal):

    @property
    def is_processing(self):
        return self._is_processing

    @is_processing.setter
    def is_processing(self, value: bool):
        self._is_processing = bool(value)
        self.redraw()

    def _generate_transaction(self) -> ProjectTransaction:
        transaction = ProjectTransaction(self.project, self.conductor)
        if self.name.value != self.project.name:
            transaction.change_name(self.name.value)
        if self.project.template_is_applicable(self.current_kernel.value):
            transaction.apply_template(self.current_kernel.value)
        for template in self.current_templates:
            if template.removed:
                transaction.rm_template(BaseTemplate.create_query(template.value.name))
            elif self.project.template_is_applicable(template.value):
                transaction.apply_template(template.value)
        return transaction

    def __init__(self, ctx: Optional[Context] = None, conductor: Optional[Conductor] = None,
                 project: Optional[Project] = None):
        super().__init__('Update a project')
        self.conductor = conductor or Conductor()
        self.click_ctx = ctx or get_current_context()
        self._is_processing = False

        self.project: Optional[Project] = project
        self.project_path = ExistingProjectParameter(
            project.location if project else os.path.join(os.path.expanduser('~'), 'My PROS Project')
        )

        self.name = parameters.Parameter(None)
        self.current_kernel: TemplateParameter = None
        self.current_templates: List[TemplateParameter] = []
        self.new_templates: List[TemplateParameter] = []

        self.templates_collapsed = parameters.BooleanParameter(False)
        self.add_template_button = components.Button('Add Template')

        @self.add_template_button.on_clicked
        def on_add_template():
            self.new_templates.append(TemplateParameter())

        cb = self.project_path.on_changed(self.project_changed, asynchronous=True)
        if self.project_path.is_valid():
            cb(self.project_path)

    def project_changed(self, new_project: ExistingProjectParameter):
        try:
            self.is_processing = True
            self.project = Project(new_project.value)

            self.name.update(self.project.project_name)

            self.current_kernel = TemplateParameter(None,
                                                    versions=sorted({
                                                        t for t in self.conductor.resolve_templates(
                                                        self.project.templates['kernel'].as_query())
                                                    }, key=lambda v: Version(v.version), reverse=True))
            self.current_templates = [
                TemplateParameter(
                    None,
                    versions=sorted({
                        t
                        for t in self.conductor.resolve_templates(t.as_query())
                    }, key=lambda v: Version(v.version), reverse=True)
                )
                for t in self.project.templates.values()
                if t.name != 'kernel'
            ]
            self.new_templates = []

            self.is_processing = False
        except BaseException as e:
            ui.logger(__name__).exception(e)

    def confirm(self, *args, **kwargs):
        self.exit()
        self._generate_transaction().execute()

    def build(self) -> Generator[components.Component, None, None]:
        yield components.DirectorySelector('Project Directory', self.project_path)
        if self.is_processing:
            yield components.Spinner()
        elif self.project_path.is_valid():
            assert self.project is not None
            yield components.Label(f'Modify your {self.project.target} project.')
            yield components.InputBox('Project Name', self.name)
            yield TemplateListingComponent(self.current_kernel, editable=dict(version=True), removable=False)
            yield components.Container(
                *(TemplateListingComponent(t, editable=dict(version=True), removable=True) for t in
                  self.current_templates),
                self.add_template_button,
                title='Templates',
                collapsed=self.templates_collapsed
            )
            yield components.Label('What will happen when you click "Continue":')
            yield components.VerbatimLabel(self._generate_transaction().describe())
