import os
import sys
import click
import prosconductor


class ArgPayload:
    def __init__(self):
        self.verbosity = 0


pass_args = click.make_pass_decorator(ArgPayload, ensure=True)


@click.group()
def conductor_cli():
    pass


@conductor_cli.group()
@click.option('--verbose', '-v', count=True)
@pass_args
def conduct(config, verbose):
    config.verbosity += verbose
    pass


@conduct.command()
@click.option('--kernel', '-k', default='latest', metavar='<version>',
              help='Specify kernel version to target.')
@click.option('--drop-in', '-d', multiple=True)
@click.option('--verbose', '-v', count=True)
@click.option('--force', '-f', is_flag=True)
@click.argument('directory', type=click.Path())
@pass_args
def create(config, kernel, drop_in, verbose, force, directory):
    config.verbosity += verbose
    click.echo(config.verbosity)
    kernels = prosconductor.resolve.resolve_kernel_request(kernel)
    if len(kernels) == 0:
        click.echo('No kernels were matched to the pattern ' + kernel +
                   ' Try a new pattern or fetching the kernel using \'pros conduct fetch ' + kernel + '\'',
                   file=sys.stderr)
        exit(1)
    elif len(kernels) == 1:
        kernel = kernels[0]
    else:
        while kernel not in kernels:
            kernel = click.prompt('Multiple kernels were matched. Please select one (' + ', '.join(kernels) + ')')
            if kernel not in kernels and config.verbosity > 0:
                click.echo('Not a valid response')
                exit(1)

    directory = os.path.normpath(os.path.expanduser(directory))
    if os.path.isfile(directory):
        if not force:
            click.confirm('Directory specified is already a file. Delete it?', abort=True)
        os.remove(directory)
    if os.path.isdir(directory) and len(os.listdir(directory)) > 0 and not force:
        click.confirm('Non-empty directory specified. Copy files regardless? ' +
                      'Note: this option will overwrite any existing files', abort=True)

    # TODO: verify drop-ins exist

    # TODO: determine kernel loader
    prosconductor.create_project(kernel, directory, drop_in)

