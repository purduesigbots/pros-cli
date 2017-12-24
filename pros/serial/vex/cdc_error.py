from .vex_device import bytes_to_str


class CDCError(Exception):
    def __init__(self, message, _tx, _rx):
        if isinstance(_tx, bytes) or isinstance(_tx, bytearray):
            _tx = bytes_to_str(_tx)
        if isinstance(_rx, bytes) or isinstance(_rx, bytearray):
            _rx = bytes_to_str(_rx)
        self.message = message
        self.tx = _tx
        self.rx = _rx

    def __str__(self):
        return "{}\nTX:{}\nRX:{}".format(self.message, self.tx, self.rx)
