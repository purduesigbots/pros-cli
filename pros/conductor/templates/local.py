from .template import Template

import tarfile
import zipfile
import os.path

def list_local_templates():
    pass


def register_local_template(path: str, origin: str) -> Template:
    if os.path.isdir(path):
        # Copy the directory
        pass
    elif zipfile.is_zipfile(path):
        # unzip
        pass
    elif tarfile.is_tarfile(path):
        # untar
        pass

    # Read template.pros and add it CLI config, set origin