from .template import Template
import os


class LocalTemplate(Template):
    def __init__(self, **kwargs):
        self.location: str = None
        super().__init__(**kwargs)

    @property
    def real_user_files(self):
        return filter(lambda f: os.path.exists(os.path.join(self.location, f)), self.user_files)

    @property
    def real_system_files(self):
        return filter(lambda f: os.path.exists(os.path.join(self.location, f)), self.system_files)

    def __hash__(self):
        return self.identifier.__hash__()

    def __eq__(self, other):
        if isinstance(other, LocalTemplate):
            return self.identifier == other.identifier
        else:
            return super().__eq__(other)
