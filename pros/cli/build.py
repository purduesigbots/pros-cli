from typing import *

import click

import pros.conductor as c
from pros.cli.common import default_options, logger, project_option, pros_root, shadow_command
from .upload import upload


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
    exit_code = project.compile(build_args)
    if exit_code != 0:
        logger(__name__).debug(f'Failed to make project: Exit Code {exit_code}')
        raise click.ClickException('Failed to build')
    return exit_code


@build_cli.command('make-upload', aliases=['mu'], hidden=True)
@click.option('build_args', '--make', '-m', multiple=True, help='Send arguments to make (e.g. compile target)')
@shadow_command(upload)
@project_option()
@click.pass_context
def make_upload(ctx, project: c.Project, build_args: List[str], **upload_args):
    ctx.invoke(make, project=project, build_args=build_args)
    ctx.invoke(upload, project=project, **upload_args)


@build_cli.command('make-upload-terminal', aliases=['mut'], hidden=True)
@click.option('build_args', '--make', '-m', multiple=True, help='Send arguments to make (e.g. compile target)')
@shadow_command(upload)
@project_option()
@click.pass_context
def make_upload_terminal(ctx, project: c.Project, build_args, **upload_args):
    from .terminal import terminal
    ctx.invoke(make, project=project, build_args=build_args)
    ctx.invoke(upload, project=project, **upload_args)
    ctx.invoke(terminal, port=project.target, request_banner=False)


@build_cli.command('build-compile-commands', hidden=True)
@project_option()
@click.option('--suppress-output/--show-output', 'suppress_output', default=False, show_default=True,
              help='Suppress output')
@click.option('--compile-commands', type=click.File('w'), default=None)
@click.option('--sandbox', default=False, is_flag=True)
@click.argument('build-args', nargs=-1)
@default_options
def build_compile_commands(project: c.Project, suppress_output: bool, compile_commands, sandbox: bool,
                           build_args: List[str]):
    """
    Build a compile_commands.json compatible with cquery
    :return:
    """
    exit_code = project.make_scan_build(build_args, cdb_file=compile_commands, suppress_output=suppress_output,
                                        sandbox=sandbox)
    if exit_code != 0:
        logger(__name__).debug(f'Failed to make project: Exit Code {exit_code}')
        raise click.ClickException('Failed to build')
    return exit_code
