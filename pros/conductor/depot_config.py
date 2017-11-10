import click
from pros.config.config import Config
import shutil
import os.path


class DepotConfig(Config):
    def __init__(self,
                 file=None, name=None, registrar=None, location=None,
                 registrar_options=None,
                 types=None,
                 root_dir=None):
        self.name = name
        self.registrar = registrar
        self.location = location
        self.types = list(types)
        self.registrar_options = registrar_options if registrar_options is not None else dict()
        if not file:
            root_dir = root_dir if root_dir is not None else click.get_app_dir('PROS')
            file = os.path.join(root_dir, name, 'depot.pros')
        super(DepotConfig, self).__init__(file)

    def delete(self):
        super(DepotConfig, self).delete()
        shutil.rmtree(self.directory)
