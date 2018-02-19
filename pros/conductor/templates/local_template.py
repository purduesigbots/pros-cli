from .template import Template


class LocalTemplate(Template):
    def __init__(self, **kwargs):
        self.location: str = None
        super().__init__(**kwargs)

    def __hash__(self):
        return self.identifier.__hash__()

    def __eq__(self, other):
        if isinstance(other, LocalTemplate):
            return self.identifier == other.identifier
        else:
            return super().__eq__(other)
