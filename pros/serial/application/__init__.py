from pros.serial.devices import GenericDevice


class Application(object):
    def __init__(self, device: GenericDevice):
        self.device = device

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def join(self):
        raise NotImplementedError
