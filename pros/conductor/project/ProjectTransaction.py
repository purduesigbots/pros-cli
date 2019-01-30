import itertools as it
import os
import tempfile
import zipfile
from typing import *

import pros.common.ui as ui
import pros.conductor as c
from pros.conductor.project.template_resolution import InvalidTemplateException, TemplateAction


class Action(object):
    def execute(self, conductor: c.Conductor, project: c.Project) -> None:
        raise NotImplementedError()

    def describe(self, conductor: c.Conductor, project: c.Project) -> str:
        raise NotImplementedError()

    def can_execute(self, conductor: c.Conductor, project: c.Project) -> bool:
        raise NotImplementedError()


class ApplyTemplateAction(Action):

    def __init__(self, template: c.BaseTemplate, apply_kwargs: Dict[str, Any] = None,
                 suppress_already_installed: bool = False):
        self.template = template
        self.apply_kwargs = apply_kwargs or {}
        self.suppress_already_installed = suppress_already_installed

    def execute(self, conductor: c.Conductor, project: c.Project):
        try:
            conductor.apply_template(project, self.template, **self.apply_kwargs)
        except InvalidTemplateException as e:
            if e.reason != TemplateAction.AlreadyInstalled or not self.suppress_already_installed:
                raise e
            else:
                ui.logger(__name__).warning(str(e))
        return None

    def describe(self, conductor: c.Conductor, project: c.Project):
        action = project.get_template_actions(conductor.resolve_template(self.template))
        if action == TemplateAction.NotApplicable:
            return f'{self.template.identifier} cannot be applied to project!'
        if action == TemplateAction.Installable:
            return f'{self.template.identifier} will installed to project.'
        if action == TemplateAction.Downgradable:
            return f'Project will be downgraded to {self.template.identifier} from' \
                f' {project.templates[self.template.name].version}.'
        if action == TemplateAction.Upgradable:
            return f'Project will be upgraded to {self.template.identifier} from' \
                f' {project.templates[self.template.name].version}.'
        if action == TemplateAction.AlreadyInstalled:
            if self.apply_kwargs.get('force_apply'):
                return f'{self.template.identifier} will be re-applied.'
            elif self.suppress_already_installed:
                return f'{self.template.identifier} will not be re-applied.'
            else:
                return f'{self.template.identifier} cannot be applied to project because it is already installed.'

    def can_execute(self, conductor: c.Conductor, project: c.Project) -> bool:
        action = project.get_template_actions(conductor.resolve_template(self.template))
        if action == TemplateAction.AlreadyInstalled:
            return self.apply_kwargs.get('force_apply') or self.suppress_already_installed
        return action in [TemplateAction.Installable, TemplateAction.Downgradable, TemplateAction.Upgradable]


class RemoveTemplateAction(Action):
    def __init__(self, template: c.BaseTemplate, remove_kwargs: Dict[str, Any] = None,
                 suppress_not_removable: bool = False):
        self.template = template
        self.remove_kwargs = remove_kwargs or {}
        self.suppress_not_removable = suppress_not_removable

    def execute(self, conductor: c.Conductor, project: c.Project):
        try:
            conductor.remove_template(project, self.template, **self.remove_kwargs)
        except ValueError as e:
            if not self.suppress_not_removable:
                raise e
            else:
                ui.logger(__name__).warning(str(e))

    def describe(self, conductor: c.Conductor, project: c.Project) -> str:
        return f'{self.template.identifier} will be removed'

    def can_execute(self, conductor: c.Conductor, project: c.Project):
        return True


class ChangeProjectNameAction(Action):
    def __init__(self, new_name: str):
        self.new_name = new_name

    def execute(self, conductor: c.Conductor, project: c.Project):
        project.project_name = self.new_name
        project.save()

    def describe(self, conductor: c.Conductor, project: c.Project):
        return f'Project will be renamed to: "{self.new_name}"'

    def can_execute(self, conductor: c.Conductor, project: c.Project):
        return True


class ProjectTransaction(object):
    def __init__(self, project: c.Project, conductor: Optional[c.Conductor] = None):
        self.project = project
        self.conductor = conductor or c.Conductor()
        self.actions: List[Action] = []

    def add_action(self, action: Action) -> None:
        self.actions.append(action)

    def execute(self):
        if len(self.actions) == 0:
            ui.logger(__name__).warning('No actions necessary.')
            return
        location = self.project.location
        tfd, tfn = tempfile.mkstemp(prefix='pros-project-', suffix=f'-{self.project.name}.zip', text='w+b')
        with os.fdopen(tfd, 'w+b') as tf:
            with zipfile.ZipFile(tf, mode='w') as zf:
                files, length = it.tee(location.glob('**/*'), 2)
                length = len(list(length))
                with ui.progressbar(files, length=length, label=f'Backing up {self.project.name} to {tfn}') as pb:
                    for file in pb:
                        zf.write(file, arcname=file.relative_to(location))

        try:
            with ui.Notification():
                for action in self.actions:
                    ui.logger(__name__).debug(action.describe(self.conductor, self.project))
                    rv = action.execute(self.conductor, self.project)
                    ui.logger(__name__).debug(f'{action} returned {rv}')
                    if rv is not None and not rv:
                        raise ValueError('Action did not complete successfully')
            ui.echo('All actions performed successfully')
        except Exception as e:
            ui.logger(__name__).warning(f'Failed to perform transaction, restoring project to previous state')

            with zipfile.ZipFile(tfn) as zf:
                with ui.progressbar(zf.namelist(), label=f'Restoring {self.project.name} from {tfn}') as pb:
                    for file in pb:
                        zf.extract(file, path=location)

            ui.logger(__name__).exception(e)
        finally:
            ui.echo(f'Removing {tfn}')
            os.remove(tfn)

    def apply_template(self, template: c.BaseTemplate, suppress_already_installed: bool = False, **kwargs):
        self.add_action(
            ApplyTemplateAction(template, suppress_already_installed=suppress_already_installed, apply_kwargs=kwargs)
        )

    def rm_template(self, template: c.BaseTemplate, suppress_not_removable: bool = False, **kwargs):
        self.add_action(
            RemoveTemplateAction(template, suppress_not_removable=suppress_not_removable, remove_kwargs=kwargs)
        )

    def change_name(self, new_name: str):
        self.add_action(ChangeProjectNameAction(new_name))

    def describe(self) -> str:
        if len(self.actions) > 0:
            return '\n'.join(
                f'- {a.describe(self.conductor, self.project)}'
                for a in self.actions
            )
        else:
            return 'No actions necessary.'

    def can_execute(self) -> bool:
        return all(a.can_execute(self.conductor, self.project) for a in self.actions)
