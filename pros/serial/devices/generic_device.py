from ..ports import BasePort


class GenericDevice(object):
    def __init__(self, port: BasePort):
        self.port = port

    def destroy(self):
        self.port.destroy()

    @property
    def name(self):
        return self.port.name
