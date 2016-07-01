from proscli.utils import default_cfg, default_options
import prosconductor.updatesite
import click
import sys


@click.group()
def conductor_cli():
    pass


@conductor_cli.group(help='Create, upgrade, and add dropins to projects.')
@default_options
def conduct():
    pass


@conduct.command('list')
@click.option('--sort-by', type=click.Choice(['kernel', 'site']), default='kernel')
@click.option('--category', type=click.Choice(['all', 'kernels', 'dropins']), default='all')
@click.argument('filter', default='.*')
@default_cfg
def list_available(cfg, sort_by, category, filter):
    if sort_by == 'kernel':
        if category == 'all' or category == 'kernels':
            click.echo('KERNEL\t\tSITES')
            for kernel in prosconductor.updatesite.get_kernels():
                click.echo('{}\t\t{}'
                           .format(kernel, ', '.join(s.id for s in prosconductor.updatesite.get_kernels()[kernel])))
            click.echo()
        if category == 'all' or category == 'dropins':
            click.echo('DROPIN\t\tSITES')
            click.echo('not yet implemented')

    pass

@conduct.command()
@default_cfg
def hello(cfg):
    # click.echo(repr(cfg.proj_cfg))
    # click.echo(repr(prosconductor.updatesite.get_kernels()))
    cfg.proj_cfg.save()


@conduct.command()
@click.option('-p', '--update-site', metavar='KEY', default=None,
              help='Specify the registrar key to download the kernel with')
@click.option('-k', '--kernel', metavar='KERNEL', default='latest', help='Specify the kernel to use.')
@click.option('-f', '--force', is_flag=True, default=False, help='Overwrite any existing files without prompt.')
@click.option('-c', '--cache', is_flag=True, default=True, help='Caches the result in the local default cache.')
@click.argument('dir', default='.')
@default_cfg
def create(cfg, force, update_site, kernel, dir):
    kernels = list(prosconductor.updatesite.get_kernels())
    kernels.sort()
    if kernel.lower() == 'latest':
        kernel = kernels[-1]
    elif kernel not in kernels:
        kernel = None
    if kernel is None:
        click.echo('Error! Kernel not found!')
        exit(1)

    options = [p.id for p in prosconductor.updatesite.get_kernels()[kernel]]
    if update_site is None:
        if len(options) > 1:
            update_site = click.prompt('Please select a update_site to obtain {} from'.format(kernel),
                                       type=click.Choice(options), show_default=True,
                                       default='cache' if 'cache' in options else options[0])
        else:
            update_site = options[0]

    if update_site not in options:
        click.echo('update_site not in available providers')
        exit(1)
    update_site = [u for u in prosconductor.updatesite.get_kernels()[kernel] if u.id == update_site][0]
    provider = prosconductor.updatesite.get_all_providers()[update_site.registrar]
    try:
        update_site.registrar_options['_force'] = force
        provider.create_proj(update_site, kernel, dir, update_site.registrar_options)
    except FileExistsError as e:
        click.echo('Error! File {} already exists! Delete it or run '
                   '\'pros {} --force\' to automatically overwrite any pre-existing files'.format(e.args[0], ' '.join(sys.argv[1:])),
                   err=True)
        exit(1)
