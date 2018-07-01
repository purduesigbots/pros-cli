import os
import tempfile
import zipfile
from datetime import datetime

import jsonpickle

import pros.common.ui as ui
from pros.common import logger
from .depot import Depot
from ..templates import BaseTemplate, ExternalTemplate


class HttpDepot(Depot):
    def __init__(self, name: str, location: str):
        super().__init__(name, location, config_schema={})

    def fetch_template(self, template: BaseTemplate, destination: str, **kwargs):
        import requests
        assert 'location' in template.metadata
        url = template.metadata['location']
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False) as tf:
                with ui.progressbar(length=int(response.headers['Content-Length']),
                                    label=f'Downloading {template.identifier} ({url})') as pb:
                    for chunk in response.iter_content(128):
                        tf.write(chunk)
                        pb.update(128)
                tf.close()
                with zipfile.ZipFile(tf.name) as zf:
                    with ui.progressbar(length=len(zf.namelist()),
                                        label=f'Extracting {template.identifier}') as pb:
                        for file in zf.namelist():
                            zf.extract(file, path=destination)
                            pb.update(1)
                os.remove(tf.name)
            return ExternalTemplate(file=os.path.join(destination, 'template.pros'))
        else:
            raise requests.ConnectionError(f'Could not obtain {url}')

    def update_remote_templates(self, **_):
        import requests
        response = requests.get(self.location)
        if response.status_code == 200:
            self.remote_templates = jsonpickle.decode(response.text)
        else:
            logger(__name__).warning(f'Unable to access {self.name} ({self.location}): {response.status_code}')
        self.last_remote_update = datetime.now()
