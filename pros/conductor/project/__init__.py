import glob
import io
import os.path
import pathlib
import sys
from pathlib import Path
from typing import *

from pros.common import *
from pros.common.ui import EchoPipe
from pros.conductor.project.template_resolution import TemplateAction
from pros.config.config import Config, ConfigNotFoundException
from .ProjectReport import ProjectReport
from ..templates import BaseTemplate, LocalTemplate, Template
from ..transaction import Transaction


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
                                                version=self.__dict__['kernel'], target=self.target,
                                                output='bin/output.bin')

    @property
    def location(self) -> pathlib.Path:
        return pathlib.Path(os.path.dirname(self.save_file))

    @property
    def path(self):
        return Path(self.location)

    @property
    def name(self):
        return self.project_name or os.path.basename(self.location) \
               or os.path.basename(self.templates['kernel'].metadata['output']) \
               or 'pros'

    @property
    def all_files(self) -> Set[str]:
        return {os.path.relpath(p, self.location) for p in
                glob.glob(f'{self.location}/**/*', recursive=True)}

    def get_template_actions(self, template: BaseTemplate) -> TemplateAction:
        ui.logger(__name__).debug(template)
        if template.target != self.target:
            return TemplateAction.NotApplicable
        from semantic_version import Spec, Version
        if template.name != 'kernel' and Version(self.kernel) not in Spec(template.supported_kernels or '>0'):
            return TemplateAction.NotApplicable
        for current in self.templates.values():
            if template.name != current.name:
                continue
            if template > current:
                return TemplateAction.Upgradable
            if template == current:
                return TemplateAction.AlreadyInstalled
            if current > template:
                return TemplateAction.Downgradable

        if any([template > current for current in self.templates.values()]):
            return TemplateAction.Upgradable
        else:
            return TemplateAction.Installable

    def template_is_installed(self, query: BaseTemplate) -> bool:
        return self.get_template_actions(query) == TemplateAction.AlreadyInstalled

    def template_is_upgradeable(self, query: BaseTemplate) -> bool:
        return self.get_template_actions(query) == TemplateAction.Upgradable

    def template_is_applicable(self, query: BaseTemplate, force_apply: bool = False) -> bool:
        ui.logger(__name__).debug(query.target)
        return self.get_template_actions(query) in (
            TemplateAction.ForcedApplicable if force_apply else TemplateAction.UnforcedApplicable)

    def apply_template(self, template: LocalTemplate, force_system: bool = False, force_user: bool = False,
                       remove_empty_directories: bool = False):
        """
        Applies a template to a project
        :param remove_empty_directories:
        :param template:
        :param force_system:
        :param force_user:
        :return:
        """
        assert template.target == self.target
        transaction = Transaction(self.location, set(self.all_files))
        installed_user_files = set()
        for lib_name, lib in self.templates.items():
            if lib_name == template.name or lib.name == template.name:
                logger(__name__).debug(f'{lib} is already installed')
                logger(__name__).debug(lib.system_files)
                logger(__name__).debug(lib.user_files)
                transaction.extend_rm(lib.system_files)
                installed_user_files = installed_user_files.union(lib.user_files)
                if force_user:
                    transaction.extend_rm(lib.user_files)

        # remove newly deprecated user files
        deprecated_user_files = installed_user_files.intersection(self.all_files) - set(template.user_files)
        if any(deprecated_user_files):
            if force_user or confirm(f'The following user files have been deprecated: {deprecated_user_files}. '
                                     f'Do you want to remove them?'):
                transaction.extend_rm(deprecated_user_files)
            else:
                logger(__name__).warning(f'Deprecated user files may cause weird quirks. See migration guidelines from '
                                         f'{template.identifier}\'s release notes.')
                # Carry forward deprecated user files into the template about to be applied so that user gets warned in
                # future.
                template.user_files.extend(deprecated_user_files)

        def new_user_filter(new_file: str) -> bool:
            """
            Filter new user files that do not have an existing friend present in the project

            Friend files are files which have the same basename
            src/opcontrol.c and src/opcontrol.cpp are friends because they have the same stem
            src/opcontrol.c and include/opcontrol.h are not because they are in different directories
            """
            return not any([(os.path.normpath(file) in transaction.effective_state) for file in template.user_files if
                            os.path.splitext(file)[0] == os.path.splitext(new_file)[0]])

        if force_user:
            new_user_files = template.real_user_files
        else:
            new_user_files = filter(new_user_filter, template.real_user_files)
        transaction.extend_add(new_user_files, template.location)

        if any([file in transaction.effective_state for file in template.system_files]) and not force_system:
            confirm(f'Some required files for {template.identifier} already exist in the project. '
                    f'Overwrite the existing files?', abort=True)
        transaction.extend_add(template.system_files, template.location)

        logger(__name__).debug(transaction)
        transaction.commit(label=f'Applying {template.identifier}', remove_empty_directories=remove_empty_directories)
        self.templates[template.name] = template
        self.save()

    def remove_template(self, template: Template, remove_user: bool = False, remove_empty_directories: bool = True):
        if not self.template_is_installed(template):
            raise ValueError(f'{template.identifier} is not installed on this project.')
        if template.name == 'kernel':
            raise ValueError(f'Cannot remove the kernel template. Maybe create a new project?')

        real_template = LocalTemplate(orig=template, location=self.location)
        transaction = Transaction(self.location, set(self.all_files))
        transaction.extend_rm(real_template.real_system_files)
        if remove_user:
            transaction.extend_rm(real_template.real_user_files)
        logger(__name__).debug(transaction)
        transaction.commit(label=f'Removing {template.identifier}...',
                           remove_empty_directories=remove_empty_directories)
        del self.templates[real_template.name]
        self.save()

    def list_template_files(self, include_system: bool = True, include_user: bool = True) -> List[str]:
        files = []
        for t in self.templates.values():
            if include_system:
                files.extend(t.system_files)
            if include_user:
                files.extend(t.user_files)
        return files

    def resolve_template(self, query: Union[str, BaseTemplate]) -> List[Template]:
        if isinstance(query, str):
            query = BaseTemplate.create_query(query)
        assert isinstance(query, BaseTemplate)
        return [local_template for local_template in self.templates.values() if local_template.satisfies(query)]

    def __str__(self):
        return f'Project: {self.location} ({self.name}) for {self.target} with ' \
            f'{", ".join([str(t) for t in self.templates.values()])}'

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

    def make(self, build_args: List[str]):
        import subprocess
        env = os.environ.copy()
        # Add PROS toolchain to the beginning of PATH to ensure PROS binaries are preferred
        if os.environ.get('PROS_TOOLCHAIN'):
            env['PATH'] = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin') + os.pathsep + env['PATH']

        # call make.exe if on Windows
        if os.name == 'nt' and os.environ.get('PROS_TOOLCHAIN'):
            make_cmd = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin', 'make.exe')
        else:
            make_cmd = 'make'
        stdout_pipe = EchoPipe()
        stderr_pipe = EchoPipe(err=True)
        process = subprocess.Popen(executable=make_cmd, args=[make_cmd, *build_args], cwd=self.directory, env=env,
                                   stdout=stdout_pipe, stderr=stderr_pipe)
        stdout_pipe.close()
        stderr_pipe.close()
        process.wait()
        return process.returncode

    def make_scan_build(self, build_args: Tuple[str], cdb_file: Optional[Union[str, io.IOBase]] = None,
                        suppress_output: bool = False, sandbox: bool = False):
        from libscanbuild.compilation import Compilation, CompilationDatabase
        from libscanbuild.arguments import create_intercept_parser
        import itertools

        import subprocess
        import argparse

        if sandbox:
            import tempfile
            td = tempfile.TemporaryDirectory()
            td_path = td.name.replace("\\", "/")
            build_args = [*build_args, f'BINDIR={td_path}']

        def libscanbuild_capture(args: argparse.Namespace) -> Tuple[int, Iterable[Compilation]]:
            """
            Implementation of compilation database generation.

            :param args:    the parsed and validated command line arguments
            :return:        the exit status of build process.
            """
            from libscanbuild.intercept import setup_environment, run_build, exec_trace_files, parse_exec_trace, \
                compilations
            from libear import temporary_directory

            with temporary_directory(prefix='intercept-') as tmp_dir:
                # run the build command
                environment = setup_environment(args, tmp_dir)
                if os.environ.get('PROS_TOOLCHAIN'):
                    environment['PATH'] = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin') + os.pathsep + \
                                          environment['PATH']

                if sys.platform == 'darwin':
                    environment['PATH'] = os.path.dirname(os.path.abspath(sys.executable)) + os.pathsep + \
                                          environment['PATH']

                if not suppress_output:
                    pipe = EchoPipe()
                else:
                    pipe = subprocess.DEVNULL
                logger(__name__).debug(self.directory)
                exit_code = run_build(args.build, env=environment, stdout=pipe, stderr=pipe, cwd=self.directory)
                if not suppress_output:
                    pipe.close()
                # read the intercepted exec calls
                calls = (parse_exec_trace(file) for file in exec_trace_files(tmp_dir))
                current = compilations(calls, args.cc, args.cxx)

                return exit_code, iter(set(current))

        # call make.exe if on Windows
        if os.name == 'nt' and os.environ.get('PROS_TOOLCHAIN'):
            make_cmd = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin', 'make.exe')
        else:
            make_cmd = 'make'
        args = create_intercept_parser().parse_args(
            ['--override-compiler', '--use-cc', 'arm-none-eabi-gcc', '--use-c++', 'arm-none-eabi-g++', make_cmd,
             *build_args,
             'CC=intercept-cc', 'CXX=intercept-c++'])
        exit_code, entries = libscanbuild_capture(args)

        if sandbox and td:
            td.cleanup()

        any_entries, entries = itertools.tee(entries, 2)
        if not any(any_entries):
            return exit_code
        if not suppress_output:
            ui.echo('Capturing metadata for PROS Editor...')
        env = os.environ.copy()
        # Add PROS toolchain to the beginning of PATH to ensure PROS binaries are preferred
        if os.environ.get('PROS_TOOLCHAIN'):
            env['PATH'] = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin') + os.pathsep + env['PATH']
        cc_sysroot = subprocess.run([make_cmd, 'cc-sysroot'], env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, cwd=self.directory)
        lines = str(cc_sysroot.stderr.decode()).splitlines() + str(cc_sysroot.stdout.decode()).splitlines()
        lines = [l.strip() for l in lines]
        cc_sysroot_includes = []
        copy = False
        for line in lines:
            if line == '#include <...> search starts here:':
                copy = True
                continue
            if line == 'End of search list.':
                copy = False
                continue
            if copy:
                cc_sysroot_includes.append(f'-isystem{line}')
        cxx_sysroot = subprocess.run([make_cmd, 'cxx-sysroot'], env=env, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, cwd=self.directory)
        lines = str(cxx_sysroot.stderr.decode()).splitlines() + str(cxx_sysroot.stdout.decode()).splitlines()
        lines = [l.strip() for l in lines]
        cxx_sysroot_includes = []
        copy = False
        for line in lines:
            if line == '#include <...> search starts here:':
                copy = True
                continue
            if line == 'End of search list.':
                copy = False
                continue
            if copy:
                cxx_sysroot_includes.append(f'-isystem{line}')
        new_entries, entries = itertools.tee(entries, 2)
        new_sources = set([e.source for e in entries])
        if not cdb_file:
            cdb_file = os.path.join(self.directory, 'compile_commands.json')
        if isinstance(cdb_file, str) and os.path.isfile(cdb_file):
            old_entries = itertools.filterfalse(lambda entry: entry.source in new_sources,
                                                CompilationDatabase.load(cdb_file))
        else:
            old_entries = []

        extra_flags = ['-target', 'armv7ar-none-none-eabi']
        logger(__name__).debug('cc_sysroot_includes')
        logger(__name__).debug(cc_sysroot_includes)
        logger(__name__).debug('cxx_sysroot_includes')
        logger(__name__).debug(cxx_sysroot_includes)

        if sys.platform == 'win32':
            extra_flags.extend(["-fno-ms-extensions", "-fno-ms-compatibility", "-fno-delayed-template-parsing"])

        def new_entry_map(entry):
            if entry.compiler == 'c':
                entry.flags = extra_flags + cc_sysroot_includes + entry.flags
            elif entry.compiler == 'c++':
                entry.flags = extra_flags + cxx_sysroot_includes + entry.flags
            return entry

        new_entries = map(new_entry_map, new_entries)

        def entry_map(entry: Compilation):
            json_entry = entry.as_db_entry()
            json_entry['arguments'][0] = 'clang' if entry.compiler == 'cc' else 'clang++'
            return json_entry

        entries = itertools.chain(old_entries, new_entries)
        json_entries = list(map(entry_map, entries))
        if isinstance(cdb_file, str):
            cdb_file = open(cdb_file, 'w')
        import json
        json.dump(json_entries, cdb_file, sort_keys=True, indent=4)

        return exit_code

    def compile(self, build_args: List[str], scan_build: Optional[bool] = None):
        if scan_build is None:
            from pros.config.cli_config import cli_config
            scan_build = cli_config().use_build_compile_commands
        return self.make_scan_build(build_args) if scan_build else self.make(build_args)

    @staticmethod
    def find_project(path: str, recurse_times: int = 10):
        path = os.path.abspath(path or '.')
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            for n in range(recurse_times):
                if path is not None and os.path.isdir(path):
                    files = [f for f in os.listdir(path)
                             if os.path.isfile(os.path.join(path, f)) and f.lower() == 'project.pros']
                    if len(files) == 1:  # found a project.pros file!
                        logger(__name__).info(f'Found Project Path: {os.path.join(path, files[0])}')
                        return os.path.join(path, files[0])
                    path = os.path.dirname(path)
                else:
                    return None
        return None


__all__ = ['Project', 'ProjectReport']
