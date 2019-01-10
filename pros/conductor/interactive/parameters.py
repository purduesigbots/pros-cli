import os.path
import sys
from typing import *

from semantic_version import Spec, Version

from pros.common.ui.interactive import parameters as p
from pros.conductor import BaseTemplate, Project


class NonExistentProjectParameter(p.ValidatableParameter[str]):
    def validate(self, value: str) -> Union[bool, str]:
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


class ExistingProjectParameter(p.ValidatableParameter[str]):
    def update(self, new_value):
        project = Project.find_project(new_value)
        if project:
            project = Project(project).directory
        super(ExistingProjectParameter, self).update(project or new_value)

    def validate(self, value: str):
        project = Project.find_project(value)
        return project is not None or 'Path is not inside a PROS project'


class TemplateParameter(p.ValidatableParameter[BaseTemplate]):
    def __init__(self, template: Optional[BaseTemplate], allow_invalid_input: bool = True, versions: Optional[List[BaseTemplate]] = None):
        version_templates: Optional[Dict[str, BaseTemplate]] = {t.version: t for t in versions}
        if not template and (not versions or len(versions) == 0):
            raise ValueError('At least template or versions must be defined for a TemplateParameter')
        if not template:
            template = version_templates[str(Spec('>0').select([Version(v) for v in version_templates.keys()]))]

        super().__init__(template, allow_invalid_input)

        self.name: p.ValidatableParameter[str] = p.ValidatableParameter(self.value.name, allow_invalid_input)
        if not self.value.version and versions:
            self.value.version = Spec('>0').select([Version(v) for v in version_templates.keys()])

        if versions:
            self.version: p.OptionParameter[str] = p.OptionParameter(self.value.version, list(version_templates.keys()))
        else:
            self.version: p.ValidatableParameter[str] = p.ValidatableParameter(self.value.version, allow_invalid_input)

        @self.name.on_any_changed
        def name_any_changed(v: p.ValidatableParameter):
            self.value.name = v.value
            self.trigger('changed', self)

        @self.version.on_any_changed
        def version_any_changed(v: p.ValidatableParameter):
            if version_templates and v.value in version_templates.keys():
                self.value = version_templates[v.value]
            else:
                self.value.version = v.value
            self.trigger('changed', self)

        self.name.on_changed(lambda v: self.trigger('changed_validated', self))
        self.version.on_changed(lambda v: self.trigger('changed_validated', self))

        self.removed = False

        @self.on('removed')
        def removed_changed():
            self.removed = not self.removed

    def is_valid(self, value: BaseTemplate = None):
        return self.name.is_valid(value.name if value else None) and \
               self.version.is_valid(value.version if value else None)
