import click
import os
import os.path
import pros.conductor
import subprocess
import sys


@click.group()
def build_cli():
    pass


@build_cli.command()
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
    if pros.conductor.Project.find_project(os.getcwd()):
        cwd = os.path.dirname(pros.conductor.Project.find_project(os.getcwd()))
    process = subprocess.Popen(executable=make_cmd, args=[make_cmd, *build_args], cwd=cwd, env=env,
                               stdout=sys.stdout, stderr=sys.stderr)
    process.wait()
    ctx.exit(process.returncode)
