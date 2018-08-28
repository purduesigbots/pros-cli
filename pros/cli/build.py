from typing import *

import click

import pros.conductor as c
from pros.cli.common import pros_root, default_options, project_option


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
        raise click.ClickException('Failed to build')
    return exit_code


@build_cli.command('make-upload', aliases=['mu'], hidden=True)
@project_option()
@click.pass_context
def make_upload(ctx, project: c.Project):
    from .upload import upload

    return ctx.forward(make, project) == 0 and ctx.forward(upload) == 0


@build_cli.command('make-upload-terminal', aliases=['mut'], hidden=True)
@project_option()
@click.pass_context
def make_upload_terminal(ctx, project: c.Project):
    from .upload import upload
    from .terminal import terminal
    return ctx.forward(make, project) == 0 and ctx.forward(upload) == 0 and ctx.forward(terminal,
                                                                                        request_banner=False) == 0


@build_cli.command('build-compile-commands', hidden=True)
@project_option()
@click.option('--suppress-output/--show-output', 'suppress_output', default=False, show_default=True,
              help='Suppress output')
@click.option('--compile-commands', type=click.File('w'), default=None)
@click.option('--sandbox', default=False, is_flag=True)
@click.argument('build-args', nargs=-1)
def build_compile_commands(project: c.Project, suppress_output: bool, compile_commands, sandbox: bool,
                           build_args: List[str]):
    """
    Build a compile_commands.json compatible with cquery
    :return:
    """
    exit_code = project.make_scan_build(build_args, cdb_file=compile_commands, suppress_output=suppress_output,
                                        sandbox=sandbox)
    if exit_code != 0:
        raise click.ClickException('Failed to build')
    return exit_code
