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


class UpdateProjectModal(application.Modal[None]):

    @property
    def is_processing(self):
        return self._is_processing

    @is_processing.setter
    def is_processing(self, value: bool):
        self._is_processing = bool(value)
        self.redraw()

    def _generate_transaction(self) -> ProjectTransaction:
        transaction = ProjectTransaction(self.project, self.conductor)
        apply_kwargs = dict(
            force_apply=self.force_apply_parameter.value
        )
        if self.name.value != self.project.name:
            transaction.change_name(self.name.value)
        if self.project.template_is_applicable(self.current_kernel.value, **apply_kwargs):
            transaction.apply_template(self.current_kernel.value, **apply_kwargs)
        for template in self.current_templates:
            if template.removed:
                transaction.rm_template(BaseTemplate.create_query(template.value.name))
            elif self.project.template_is_applicable(template.value, **apply_kwargs):
                transaction.apply_template(template.value, **apply_kwargs)
        for template in self.new_templates:
            if not template.removed:  # template should never be "removed"
                transaction.apply_template(template.value, force_apply=self.force_apply_parameter.value)
        return transaction

    def _add_template(self):
        options = self.conductor.resolve_templates(identifier=BaseTemplate(target=self.project.target), unique=True)
        ui.logger(__name__).debug(options)
        p = TemplateParameter(None, options)

        @p.on('removed')
        def remove_template():
            self.new_templates.remove(p)

        self.new_templates.append(p)

    def __init__(self, ctx: Optional[Context] = None, conductor: Optional[Conductor] = None,
                 project: Optional[Project] = None):
        super().__init__('Update a project')
        self.conductor = conductor or Conductor()
        self.click_ctx = ctx or get_current_context()
        self._is_processing = False

        self.project: Optional[Project] = project
        self.project_path = ExistingProjectParameter(
            str(project.location) if project else os.path.join(os.path.expanduser('~'), 'My PROS Project')
        )

        self.name = parameters.Parameter(None)
        self.current_kernel: TemplateParameter = None
        self.current_templates: List[TemplateParameter] = []
        self.new_templates: List[TemplateParameter] = []
        self.force_apply_parameter = parameters.BooleanParameter(False)

        self.templates_collapsed = parameters.BooleanParameter(False)
        self.advanced_collapsed = parameters.BooleanParameter(True)

        self.add_template_button = components.Button('Add Template')

        self.add_template_button.on_clicked(self._add_template)

        cb = self.project_path.on_changed(self.project_changed, asynchronous=True)
        if self.project_path.is_valid():
            cb(self.project_path)

    def project_changed(self, new_project: ExistingProjectParameter):
        try:
            self.is_processing = True
            self.project = Project(new_project.value)

            self.name.update(self.project.project_name)

            self.current_kernel = TemplateParameter(
                None,
                options=sorted(
                    {t for t in self.conductor.resolve_templates(self.project.templates['kernel'].as_query())},
                    key=lambda v: Version(v.version), reverse=True
                )
            )
            self.current_templates = [
                TemplateParameter(
                    None,
                    options=sorted({
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

    @property
    def can_confirm(self):
        return self.project and self._generate_transaction().can_execute()

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
                *(TemplateListingComponent(t, editable=True, removable=True) for t in self.new_templates),
                self.add_template_button,
                title='Templates',
                collapsed=self.templates_collapsed
            )
            yield components.Container(
                components.Checkbox('Re-apply all templates', self.force_apply_parameter),
                title='Advanced',
                collapsed=self.advanced_collapsed
            )
            yield components.Label('What will happen when you click "Continue":')
            yield components.VerbatimLabel(self._generate_transaction().describe())
