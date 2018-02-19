import glob
import os.path
from typing import *

from pros.common import *
from pros.conductor import LocalTemplate, Template, BaseTemplate
from pros.config.config import Config, ConfigNotFoundException
from .transaction import Transaction


class Project(Config):
    def __init__(self, path: str = '.', create: bool = False, raise_on_error: bool = True, defaults: dict = None):
        """
        Instantiates a PROS project configuration
        :param path: A path to the project, may be the actual project.pros file, any child directory of the project,
        or the project directory itself. See Project.find_project for more details
        :param create: The default implementation of this initializer is to raise a ConfigNotFoundException if the
        project was not found. Create allows
        :param raise_on_error:
        :param defaults:
        """
        file = Project.find_project(path or '.')
        if file is None and create:
            file = os.path.join(path, 'project.pros') if not os.path.basename(path) == 'project.pros' else path
        elif file is None and raise_on_error:
            raise ConfigNotFoundException('A project config was not found for {}'.format(path))

        if defaults is None:
            defaults = {}
        self.target: str = defaults.get('target', 'cortex').lower()  # VEX Hardware target (V5/Cortex)
        self.templates: Dict[str, Template] = defaults.get('templates', {})
        self.upload_options: Dict = defaults.get('upload_options', {})
        self.project_name: str = defaults.get('project_name', None)
        super(Project, self).__init__(file, error_on_decode=raise_on_error)
        if 'kernel' in self.__dict__:
            # Add backwards compatibility with PROS CLI 2 projects by adding kernel as a pseudo-template
            self.templates['kernel'] = Template(user_files=self.all_files, name='kernel',
                                                version=self.__dict__['kernel'], target=self.target)

    @property
    def location(self):
        return os.path.dirname(self.save_file)

    @property
    def name(self):
        return self.project_name or os.path.basename(self.location) or \
               os.path.basename(self.templates['kernel'].metadata['output']) or 'pros'

    @property
    def all_files(self) -> Set[str]:
        return {os.path.relpath(p, self.location) for p in
                glob.glob(f'{self.location}/**/*', recursive=True)}

    def template_is_installed(self, query: BaseTemplate) -> bool:
        return any([t.satisfies(query) for t in self.templates.values()])

    def template_is_upgradeable(self, query: BaseTemplate) -> bool:
        return any([query > t for t in self.templates.values()])

    def apply_template(self, template: LocalTemplate, force_system: bool = False, force_user: bool = False):
        """
        Applies a template to a project
        :param template:
        :param force_system:
        :param force_user:
        :return:
        """
        transaction = Transaction(self.location, set(self.all_files))
        installed_user_files = set()
        for lib_name, lib in self.templates.items():
            if lib_name == template.name or lib.name == template.name:
                transaction.extend_rm(template.system_files)
                installed_user_files = installed_user_files.union(template.user_files)
                if force_user:
                    transaction.extend_rm(template.user_files)

        # remove newly deprecated user files
        deprecated_user_files = installed_user_files - set(template.user_files)
        if any(deprecated_user_files) and not force_user:
            confirm(f'The following user files have been deprecated: {deprecated_user_files}. '
                    f'Do you want to remove them?', abort=True)
        transaction.extend_rm(deprecated_user_files)

        def new_user_filter(new_file: str) -> bool:
            """
            Filter new user files that do not have an existing friend present in the project

            Friend files are files which have the same basename
            src/opcontrol.c and src/opcontrol.cpp are friends because they have the same stem
            src/opcontrol.c and include/opcontrol.h are not because they are in different directories
            """
            return not any([os.path.normpath(file) in transaction.effective_state for file in template.user_files if
                            os.path.splitext(file)[0] == os.path.splitext(new_file)[0]])

        if force_user:
            new_user_files = template.user_files
        else:
            new_user_files = filter(new_user_filter, template.real_user_files)
        transaction.extend_add(new_user_files, template.location)

        if any([file in transaction.effective_state for file in template.system_files]) and not force_system:
            confirm(f'Some required files for {template.identifier} already exist in the project. '
                    f'Overwrite the existing files?', abort=True)
        transaction.extend_add(template.system_files, template.location)

        logger(__name__).debug(transaction)
        transaction.commit(label=f'Applying {template.identifier}')
        self.templates[template.name] = template
        self.save()

    def list_template_files(self, include_system: bool = True, include_user: bool = True) -> List[str]:
        files = []
        for t in self.templates.values():
            if include_system:
                files.extend(t.system_files)
            if include_user:
                files.extend(t.user_files)
        return files

    def __str__(self):
        return f'Project: {self.location} ({self.name}) for {self.target} with {", ".join([str(t) for t in self.templates.values()])}'

    @property
    def kernel(self):
        if 'kernel' in self.templates:
            return self.templates['kernel'].version
        elif hasattr(self.__dict__, 'kernel'):
            return self.__dict__['kernel']
        return ''

    @property
    def output(self):
        if 'kernel' in self.templates:
            return self.templates['kernel'].metadata['output']
        elif hasattr(self.__dict__, 'output'):
            return self.__dict__['output']
        return 'bin/output.bin'

    @staticmethod
    def find_project(path: str, recurse_times: int = 10):
        path = os.path.abspath(path)
        if os.path.isfile(path):
            return path
        elif os.path.isdir(path):
            for n in range(recurse_times):
                if path is not None and os.path.isdir(path):
                    files = [f for f in os.listdir(path)
                             if os.path.isfile(os.path.join(path, f)) and f.lower() == 'project.pros']
                    if len(files) == 1:  # found a project.pros file!
                        return os.path.join(path, files[0])
                    path = os.path.dirname(path)
                else:
                    return None
        return None
