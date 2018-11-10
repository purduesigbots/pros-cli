import os.path
import sys

from typing import *

from pros.common.ui.interactive import parameters
from pros.conductor import Project


class NonExistentProjectParameter(parameters.ValidatableParameter[str]):
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


class ExistingProjectParameter(parameters.ValidatableParameter[str]):
    def update(self, new_value):
        project = Project.find_project(new_value)
        if project:
            project = Project(project).directory
        super(ExistingProjectParameter, self).update(project or new_value)

    def validate(self, value: str):
        project = Project.find_project(value)
        return project is not None or 'Path is not inside a PROS project'