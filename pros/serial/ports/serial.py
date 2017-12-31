from typing import *

import serial

from pros.common import *
from pros.serial import bytes_to_str
from .port import Port


def create_serial_port(port_name: str, timeout: Optional[float] = 0.5) -> serial.Serial:
    port = serial.Serial(port_name, baudrate=115200, bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    port.timeout = timeout
    port.inter_byte_timeout = 0.2
    return port


class SerialPort(Port):
    def __init__(self, port_name: str, timeout: Optional[float] = 0.5):
        self.port = create_serial_port(port_name=port_name, timeout=timeout)
        self.port_name = port_name
        if not self.port.is_open:
            self.port.open()
        logger(self).debug('Created SerialPort connected to {}'.format(port_name))

    def write(self, data: AnyStr):
        if isinstance(data, str):
            data = data.encode(encoding='ascii')
        assert (isinstance(data, bytes))
        return self.port.write(data)

    def read(self, n_bytes: int = -1):
        if n_bytes < 1:
            return self.port.read_all()
        else:
            return self.port.read(n_bytes)

    def flush(self):
        return self.port.flush()
