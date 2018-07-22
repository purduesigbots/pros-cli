import os
import os.path

import click

import pros.conductor as c
from pros.cli.common import pros_root, logger, default_options, project_option


@pros_root
def build_cli():
    pass


@build_cli.command(aliases=['build'])
@project_option()
@click.argument('build-args', nargs=-1)
@default_options
def make(project: c.Project, build_args):
    """
    Build current PROS project or cwd
    """
    return project.compile(build_args)


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
    project_path = c.Project.find_project(os.getcwd())
    if not project_path:
        logger(__name__).error('You must be inside a PROS project to invoke this command')
        return -1
    return c.Project(project_path).compile(build_args, scan_build=True)
