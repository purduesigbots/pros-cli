import os.path
import shutil
import zipfile

import click

from pros.config import ConfigNotFoundException
from .depot import Depot
from ..templates import BaseTemplate, Template, ExternalTemplate
from pros.common.utils import logger


class LocalDepot(Depot):
    def fetch_template(self, template: BaseTemplate, destination: str, **kwargs) -> Template:
        if 'location' not in kwargs:
            logger(__name__).debug(f"Template not specified. Provided arguments: {kwargs}")
            raise KeyError('Location of local template must be specified.')
        location = kwargs['location']
        if os.path.isdir(location):
            location_dir = location
            if not os.path.isfile(os.path.join(location_dir, 'template.pros')):
                raise ConfigNotFoundException(f'A template.pros file was not found in {location_dir}.')
            template_file = os.path.join(location_dir, 'template.pros')
        elif zipfile.is_zipfile(location):
            with zipfile.ZipFile(location) as zf:
                with click.progressbar(length=len(zf.namelist()),
                                       label=f"Extracting {location}") as progress_bar:
                    for file in zf.namelist():
                        zf.extract(file, path=destination)
                        progress_bar.update(1)
            template_file = os.path.join(destination, 'template.pros')
            location_dir = destination
        elif os.path.isfile(location):
            location_dir = os.path.dirname(location)
            template_file = location
        elif isinstance(template, ExternalTemplate):
            location_dir = template.directory
            template_file = template.save_file
        else:
            raise ValueError(f"The specified location was not a file or directory ({location}).")
        if location_dir != destination:
            n_files = len([os.path.join(dp, f) for dp, dn, fn in os.walk(location_dir) for f in fn])
            with click.progressbar(length=n_files, label='Copying to local cache') as pb:
                def my_copy(*args):
                    pb.update(1)
                    shutil.copy2(*args)

                shutil.copytree(location_dir, destination, copy_function=my_copy)
        return ExternalTemplate(file=template_file)

    def __init__(self):
        super().__init__('local', 'local')
