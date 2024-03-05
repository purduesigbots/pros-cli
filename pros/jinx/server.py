from pros.serial.devices import StreamDevice


class JinxServer:
    def __init__(self, device: StreamDevice):
        self.device = device
