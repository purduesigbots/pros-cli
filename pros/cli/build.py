import os
import os.path
import subprocess
import sys
from typing import *

import click

import pros.conductor as c
from .click_classes import PROSGroup


@click.group(cls=PROSGroup)
def build_cli():
    pass


@build_cli.command(aliases=['build'])
@click.argument('build-args', nargs=-1)
@click.pass_context
def make(ctx, build_args):
    """
    Build current PROS project or cwd
    """
    env = os.environ.copy()
    # Add PROS toolchain to the beginning of PATH to ensure PROS binaries are preferred
    if os.environ.get('PROS_TOOLCHAIN'):
        env['PATH'] = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin') + os.pathsep + env['PATH']

    # call make.exe if on Windows
    if os.name == 'nt' and os.environ.get('PROS_TOOLCHAIN'):
        make_cmd = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin', 'make.exe')
    else:
        make_cmd = 'make'
    cwd = os.getcwd()
    if c.Project.find_project(os.getcwd()):
        cwd = os.path.dirname(c.Project.find_project(os.getcwd()))
    process = subprocess.Popen(executable=make_cmd, args=[make_cmd, *build_args], cwd=cwd, env=env,
                               stdout=sys.stdout, stderr=sys.stderr)
    process.wait()
    if process.returncode != 0:
        ctx.exit(process.returncode)


@build_cli.command('make-upload', aliases=['mu'], hidden=True)
@click.pass_context
def make_upload(ctx):
    from .upload import upload
    ctx.forward(make)
    ctx.forward(upload)


@build_cli.command('make-upload-terminal', aliases=['mut'], hidden=True)
@click.pass_context
def make_upload_terminal(ctx):
    from .upload import upload
    from .terminal import terminal
    ctx.forward(make)
    ctx.forward(upload)
    ctx.forward(terminal, request_banner=False)


@build_cli.command('build-compile-commands', hidden=True)
@click.argument('build-args', nargs=-1)
def build_compile_commands(build_args):
    """
    Build a compile_commands.json compatible with cquery
    :return:
    """
    from libscanbuild.compilation import Compilation, CompilationDatabase
    from libscanbuild.arguments import create_intercept_parser
    from tempfile import TemporaryDirectory
    import itertools

    def libscanbuild_capture(args):
        import argparse
        from libscanbuild.intercept import setup_environment, run_build, exec_trace_files, parse_exec_trace, \
            compilations
        from libear import temporary_directory
        # type: argparse.Namespace -> Tuple[int, Iterable[Compilation]]
        """ Implementation of compilation database generation.
        :param args:    the parsed and validated command line arguments
        :return:        the exit status of build process. """

        with temporary_directory(prefix='intercept-') as tmp_dir:
            # run the build command
            environment = setup_environment(args, tmp_dir)
            if os.environ.get('PROS_TOOLCHAIN'):
                environment['PATH'] = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin') + os.pathsep + environment[
                    'PATH']
            exit_code = run_build(args.build, env=environment)
            # read the intercepted exec calls
            calls = (parse_exec_trace(file) for file in exec_trace_files(tmp_dir))
            current = compilations(calls, args.cc, args.cxx)

            return exit_code, iter(set(current))

    # call make.exe if on Windows
    if os.name == 'nt' and os.environ.get('PROS_TOOLCHAIN'):
        make_cmd = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin', 'make.exe')
    else:
        make_cmd = 'make'
    with TemporaryDirectory() as td:
        bindir = td.replace("\\", "/") if os.sep == '\\' else td
        args = create_intercept_parser().parse_args(
            ['--override-compiler', '--use-cc', 'arm-none-eabi-gcc', '--use-c++', 'arm-none-eabi-g++', make_cmd,
             *build_args,
             'CC=intercept-cc', 'CXX=intercept-c++'])
        exit_code, entries = libscanbuild_capture(args)

    import subprocess
    env = os.environ.copy()
    # Add PROS toolchain to the beginning of PATH to ensure PROS binaries are preferred
    if os.environ.get('PROS_TOOLCHAIN'):
        env['PATH'] = os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin') + os.pathsep + env['PATH']
    cc_sysroot = subprocess.run([make_cmd, 'cc-sysroot'], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = str(cc_sysroot.stdout.decode()).splitlines()
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
    cxx_sysroot = subprocess.run([make_cmd, 'cxx-sysroot'], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = str(cxx_sysroot.stdout.decode()).splitlines()
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
    if os.path.isfile(args.cdb):
        old_entries = itertools.filterfalse(lambda entry: entry.source in new_sources, CompilationDatabase.load(args.cdb))
    else:
        old_entries = []

    extra_flags = ['-target', 'armv7ar-none-none-eabi']

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
    with open(args.cdb, 'w') as handle:
        import json
        json.dump(json_entries, handle, sort_keys=True, indent=4)

    return exit_code
