import prosconductor.updatesite.genericprovider
import os
import click
import proscli.utils
import prosconfig
import shutil


class LocalProvider(prosconductor.updatesite.genericprovider.UpdateSiteProvider):
    @staticmethod
    def get_key():
        return 'cache'

    @staticmethod
    def get_kernels(site):
        if not os.path.isdir(os.path.join(site.uri, 'kernels')):
            return []
        return [k for k in os.listdir(os.path.join(site.uri, 'kernels'))
                if os.path.isdir(os.path.join(site.uri, 'kernels', k))]

    @staticmethod
    def create_proj(site, kernel, destination, options):
        if '_force' not in options:
            options['_force'] = False
        state = prosconfig.get_state()
        if kernel not in LocalProvider.get_kernels(site):
            proscli.utils.debug('Available kernels: {}'.format(LocalProvider.get_kernels(site)))
            click.echo('Error! Kernel ({}) does not exist on {} (via provider {})'
                       .format(kernel, site.uri, LocalProvider.get_key()))

        for root, dirs, files in os.walk(os.path.join(site.uri, 'kernels', kernel)):
            relpath = os.path.relpath(root, os.path.join(site.uri, 'kernels', kernel))
            if relpath == os.path.join('', '.'):  # sensible renaming so that we don't get weird looking output
                relpath = ''
            dest_path = os.path.join(destination, relpath)
            for dir in dirs:
                if state.verbosity > 0:
                    click.echo('Creating directory {}'.format(os.path.join(dest_path, dir)))
                os.makedirs(os.path.join(dest_path, dir), exist_ok=True)
            for file in files:
                if os.path.isfile(os.path.join(dest_path, file)) and not options['_force']:
                    if not click.confirm('Warning! File {} already exists! Overwrite it? '
                                         .format(os.path.join(dest_path, file)), default=False):
                        raise FileExistsError(os.path.join(dest_path, file))
                    else:
                        click.echo('Hint: run with --force to disable this prompt\n')
                if state.verbosity > 0:
                    click.echo('Copying file {} -> {}'
                               .format(os.path.join(relpath, file), os.path.join(dest_path, file)))
                shutil.copy2(os.path.join(root, file), os.path.join(dest_path, file))
