import os
import zipfile
from datetime import datetime

import jsonpickle

import pros.common.ui as ui
from pros.common import logger
from pros.common.utils import download_file
from .depot import Depot
from ..templates import BaseTemplate, ExternalTemplate


class HttpDepot(Depot):
    def __init__(self, name: str, location: str):
        super().__init__(name, location, config_schema={})

    def fetch_template(self, template: BaseTemplate, destination: str, **kwargs):
        import requests
        assert 'location' in template.metadata
        url = template.metadata['location']
        tf = download_file(url, ext='zip', desc=f'Downloading {template.identifier}')
        if tf is None:
            raise requests.ConnectionError(f'Could not obtain {url}')
        with zipfile.ZipFile(tf) as zf:
            with ui.progressbar(length=len(zf.namelist()),
                                label=f'Extracting {template.identifier}') as pb:
                for file in zf.namelist():
                    zf.extract(file, path=destination)
                    pb.update(1)
        os.remove(tf)
        return ExternalTemplate(file=os.path.join(destination, 'template.pros'))

    def update_remote_templates(self, **_):
        import requests
        response = requests.get(self.location)
        if response.status_code == 200:
            self.remote_templates = jsonpickle.decode(response.text)
        else:
            logger(__name__).warning(f'Unable to access {self.name} ({self.location}): {response.status_code}')
        self.last_remote_update = datetime.now()
