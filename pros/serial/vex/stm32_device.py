import time
from typing import *
from serial import Serial
from .vex_device import debug


class STM32Device(object):
    ACK_BYTE = 0x76
    NACK_BYTE = 0xFF

    def __init__(self, port: Serial, debug_print: Callable[[str], None] = debug):
        self.port = port
        if not self.port.is_open:
            self.port.open()
        self.debug_print = debug_print

        self._txrx_command(0x7f)

    def erase_flash(self):
        pass

    def _txrx_command(self, command: Union[int, bytes, bytearray], retries: int=5, timeout: float=0.01):
        try:
            self.port.read_all()
            self.port.write(command)
            self.port.flush()
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.port.read(1)[0] == self.ACK_BYTE:
                    return
            raise IOError("Device never ACK'd")
        except BaseException as e:
            if retries > 0:
                self._txrx_command(command, retries=retries-1, timeout=timeout)
            else:
                raise e