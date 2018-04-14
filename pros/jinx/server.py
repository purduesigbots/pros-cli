from pros.serial.devices import StreamDevice


class JinxServer(object):
    def __init__(self, device: StreamDevice):
        self.device = device
