import click
import subprocess
import sys
import os
# import prosconfig
import proscli.flasher


@click.group()
def build_cli():
    pass


@build_cli.command()
@click.argument('build-args', nargs=-1)
@click.pass_context
def make(ctx, build_args):
    """Invokes make.

    If on Windows, will invoke make located in on the PROS_TOOLCHAIN.

    Also has the added benefit of looking for the config.pros file"""
    click.echo('Invoking make...')
    # cfg = prosconfig.find_project('.')
    cwd = '.'
    # if cfg is not None:
    #     cwd = cfg.path
    cmd = (os.path.join(os.environ.get('PROS_TOOLCHAIN'), 'bin', 'make.exe') if os.name == 'nt' else 'make')
    if os.path.exists(cmd):
        p = subprocess.Popen(executable=cmd, args=build_args, cwd=cwd,
                             stdout=sys.stdout, stderr=sys.stderr)
        p.wait()
        if p.returncode != 0:
            ctx.exit(1)
    else:
        click.echo('Error... make not found.', err=True)
        ctx.exit(1)


@build_cli.command(name='mu', help='Combines \'make\' and \'flash\'')
@click.argument('build-args', nargs=-1)
@click.pass_context
def make_flash(ctx, build_args):
    ctx.invoke(make, build_args=build_args)
    ctx.invoke(proscli.flasher.flash)
