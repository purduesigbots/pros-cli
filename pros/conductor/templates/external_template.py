import os.path
import tempfile
import zipfile

from pros.config import Config

from .template import Template


class ExternalTemplate(Config, Template):
    def __init__(self, file: str, **kwargs):
        if os.path.isdir(file):
            file = os.path.join(file, 'template.pros')
        elif zipfile.is_zipfile(file):
            self.tf = tempfile.NamedTemporaryFile(delete=False)
            with zipfile.ZipFile(file) as zf:
                with zf.open('template.pros') as zt:
                    self.tf.write(zt.read())
            self.tf.seek(0, 0)
            file = self.tf.name
        error_on_decode = kwargs.pop('error_on_decode', False)
        Template.__init__(self, **kwargs)
        Config.__init__(self, file, error_on_decode=error_on_decode)

    def __del__(self):
        if hasattr(self, 'tr'):
            del self.tf
