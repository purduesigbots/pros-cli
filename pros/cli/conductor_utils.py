import glob
import os.path
import re
import tempfile
import zipfile
from typing import *

import click
import pros.common.ui as ui
import pros.conductor as c
from pros.common.utils import logger
from pros.conductor.templates import ExternalTemplate

from .common import default_options, template_query
from .conductor import conductor


@conductor.command('create-template', context_settings={'allow_extra_args': True, 'ignore_unknown_options': True})
@click.argument('path', type=click.Path(exists=True))
@click.argument('name')
@click.argument('version')
@click.option('--system', 'system_files', multiple=True, type=click.Path(),
              help='Specify "system" files required by the template')
@click.option('--user', 'user_files', multiple=True, type=click.Path(),
              help='Specify files that are intended to be modified by users')
@click.option('--kernels', 'supported_kernels', help='Specify supported kernels')
@click.option('--target', type=click.Choice(['v5', 'cortex']), help='Specify the target platform (cortex or v5)')
@click.option('--destination', type=click.Path(),
              help='Specify an alternate destination for the created ZIP file or template descriptor')
@click.option('--zip/--no-zip', 'do_zip', default=True, help='Create a ZIP file or create a template descriptor.')
@default_options
@click.pass_context
def create_template(ctx, path: str, destination: str, do_zip: bool, **kwargs):
    """
    Create a template to be used in other projects

    Templates primarily consist of the following fields: name, version, and
    files to install.

    Templates have two types of files: system files and user files. User files
    are files in a template intended to be modified by users - they are not
    replaced during upgrades or removed by default when a library is uninstalled.
    System files are files that are for the "system." They get replaced every
    time the template is upgraded. The default PROS project is a template. The user
    files are files like src/opcontrol.c and src/initialize.c, and the system files
    are files like firmware/libpros.a and include/api.h.

    You should specify the --system and --user options multiple times to include
    more than one file. Both flags also accept glob patterns. When a glob pattern is
    provided and inside a PROS project, then all files that match the pattern that
    are NOT supplied by another template are included.


    Example usage:

    pros conduct create-template . libblrs 2.0.1 --system "firmware/*.a" --system "include/*.h"
    """
    project = c.Project.find_project(path, recurse_times=1)
    if project:
        project = c.Project(project)
        path = project.location
        if not kwargs['supported_kernels'] and kwargs['name'] != 'kernel':
            kwargs['supported_kernels'] = f'^{project.kernel}'
        kwargs['target'] = project.target
    if not destination:
        if os.path.isdir(path):
            destination = path
        else:
            destination = os.path.dirname(path)
    kwargs['system_files'] = list(kwargs['system_files'])
    kwargs['user_files'] = list(kwargs['user_files'])
    kwargs['metadata'] = {ctx.args[i][2:]: ctx.args[i + 1] for i in range(0, int(len(ctx.args) / 2) * 2, 2)}

    def get_matching_files(globs: List[str]) -> Set[str]:
        matching_files: List[str] = []
        _path = os.path.normpath(path) + os.path.sep
        for g in [g for g in globs if glob.has_magic(g)]:
            files = glob.glob(f'{path}/{g}', recursive=True)
            files = filter(lambda f: os.path.isfile(f), files)
            files = [os.path.normpath(os.path.normpath(f).split(_path)[-1]) for f in files]
            matching_files.extend(files)

        # matches things like src/opcontrol.{c,cpp} so that we can expand to src/opcontrol.c and src/opcontrol.cpp
        pattern = re.compile(r'^([\w{}]+.){{((?:\w+,)*\w+)}}$'.format(os.path.sep.replace('\\', '\\\\')))
        for f in [os.path.normpath(f) for f in globs if not glob.has_magic(f)]:
            if re.match(pattern, f):
                matches = re.split(pattern, f)
                logger(__name__).debug(f'Matches on {f}: {matches}')
                matching_files.extend([f'{matches[1]}{ext}' for ext in matches[2].split(',')])
            else:
                matching_files.append(f)

        matching_files: Set[str] = set(matching_files)
        return matching_files

    matching_system_files: Set[str] = get_matching_files(kwargs['system_files'])
    matching_user_files: Set[str] = get_matching_files(kwargs['user_files'])

    matching_system_files: Set[str] = matching_system_files - matching_user_files

    # exclude existing project.pros and template.pros from the template,
    # and name@*.zip so that we don't redundantly include ZIPs
    exclude_files = {'project.pros', 'template.pros', *get_matching_files([f"{kwargs['name']}@*.zip"])}
    if project:
        exclude_files = exclude_files.union(project.list_template_files())
    matching_system_files = matching_system_files - exclude_files
    matching_user_files = matching_user_files - exclude_files

    def filename_remap(file_path: str) -> str:
        if os.path.dirname(file_path) == 'bin':
            return file_path.replace('bin', 'firmware', 1)
        return file_path

    kwargs['system_files'] = list(map(filename_remap, matching_system_files))
    kwargs['user_files'] = list(map(filename_remap, matching_user_files))

    if do_zip:
        if not os.path.isdir(destination) and os.path.splitext(destination)[-1] != '.zip':
            logger(__name__).error(f'{destination} must be a zip file or an existing directory.')
            return -1
        with tempfile.TemporaryDirectory() as td:
            template = ExternalTemplate(file=os.path.join(td, 'template.pros'), **kwargs)
            template.save()
            if os.path.isdir(destination):
                destination = os.path.join(destination, f'{template.identifier}.zip')
            with zipfile.ZipFile(destination, mode='w') as z:
                z.write(template.save_file, arcname='template.pros')

                for file in matching_user_files:
                    source_path = os.path.join(path, file)
                    dest_file = filename_remap(file)
                    if os.path.exists(source_path):
                        ui.echo(f'U: {file}' + (f' -> {dest_file}' if file != dest_file else ''))
                        z.write(f'{path}/{file}', arcname=dest_file)
                for file in matching_system_files:
                    source_path = os.path.join(path, file)
                    dest_file = filename_remap(file)
                    if os.path.exists(source_path):
                        ui.echo(f'S: {file}' + (f' -> {dest_file}' if file != dest_file else ''))
                        z.write(f'{path}/{file}', arcname=dest_file)
    else:
        if os.path.isdir(destination):
            destination = os.path.join(destination, 'template.pros')
        template = ExternalTemplate(file=destination, **kwargs)
        template.save()


@conductor.command('purge-template', help='Purge template(s) from the local cache',
                   context_settings={'ignore_unknown_options': True})
@click.option('-f', '--force', is_flag=True, default=False, help='Do not prompt for removal of multiple templates')
@template_query(required=False)
@default_options
def purge_template(query: c.BaseTemplate, force):
    if not query:
        force = click.confirm('Are you sure you want to remove all cached templates? This action is non-reversable!',
                              abort=True)
    cond = c.Conductor()
    templates = cond.resolve_templates(query, allow_online=False)
    if len(templates) == 0:
        click.echo('No matching templates were found matching the spec.')
        return 0
    click.echo(f'The following template(s) will be removed {[t.identifier for t in templates]}')
    if len(templates) > 1 and not force:
        click.confirm(f'Are you sure you want to remove multiple templates?', abort=True)
    for template in templates:
        if isinstance(template, c.LocalTemplate):
            cond.purge_template(template)
