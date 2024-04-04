import os
import zipfile
from datetime import datetime
import json

import jsonpickle

import pros.common.ui as ui
from pros.common import logger
from pros.common.utils import download_file
from .http_depot import HttpDepot
from ..templates import BaseTemplate, ExternalTemplate

BRANCHLINE_URL = 'https://pros.cs.purdue.edu/v5/_static/branchline/pros-branchline.json'


class BranchlineDepot(HttpDepot):
    def __init__(self, name: str, location: str):
        super().__init__(name, location)

    def fetch_template(self, template: BaseTemplate, destination: str, version: str, **kwargs):
        import requests
        assert 'location' in template.metadata
        version_url = BRANCHLINE_URL[:-1] + template.metadata['location']
        versions_response = requests.get(version_url)
        url: str = None
        if versions_response.status_code == 200:
            versions = jsonpickle.decode(versions_response.text)
            for version in versions:
                if version['version'] == version:
                    url = version['metadata']['location']
                    break
        else:
            logger(__name__).warning(f'Unable to access versions for {template.name} ({template.version}): {versions_response.status_code}')
            raise requests.ConnectionError(f'Could not obtain versions file for {template.name} ({template.version}). HTTP status code: {versions_response.status_code}')

        tf = download_file(url, ext='zip', desc=f'Downloading {template.identifier}')
        if tf is None:
            raise requests.ConnectionError(f'Could not obtain {version_url}')
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
            parent_templates = json.loads(response.text)
            for parent_template in parent_templates:
                version_url = '/'.join(BRANCHLINE_URL.split('/')[:-1]) + '/' + parent_template['metadata']['versions']
                versions_response = requests.get(version_url)
                if versions_response.status_code == 200:
                    versions = json.loads(versions_response.text)
                    for version in versions:
                        self.remote_templates.append(BaseTemplate(name=parent_template['name'], version=version['version'], metadata=version['metadata'], supported_kernels=version['supported_kernels']))
                else:
                    logger(__name__).warning(f'Unable to access versions for {parent_template["name"]} ({parent_template["metadata"]["versions"]}): {versions_response.status_code}')
        else:
            logger(__name__).warning(f'Unable to access {self.name} ({self.location}): {response.status_code}')
        self.last_remote_update = datetime.now()
