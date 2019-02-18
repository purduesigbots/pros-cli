import sys
from typing import *

import serial

from pros.common import logger, dont_send
from pros.serial.ports.exceptions import ConnectionRefusedException
from .base_port import BasePort, PortConnectionException


def create_serial_port(port_name: str, timeout: Optional[float] = 1.0) -> serial.Serial:
    try:
        logger(__name__).debug(f'Opening serial port {port_name}')
        port = serial.Serial(port_name, baudrate=115200, bytesize=serial.EIGHTBITS,
                             parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        port.timeout = timeout
        port.inter_byte_timeout = 0.2
        return port
    except serial.SerialException as e:
        if any(msg in str(e) for msg in [
            'Access is denied', 'Errno 16', 'Errno 13'
        ]):
            tb = sys.exc_info()[2]
            raise dont_send(ConnectionRefusedException(port_name, e).with_traceback(tb))
        else:
            raise e


class DirectPort(BasePort):

    def __init__(self, port_name: str, **kwargs):
        self.serial: serial.Serial = create_serial_port(port_name=port_name, timeout=kwargs.pop('timeout', 1.0))
        self.buffer: bytearray = bytearray()

    def read(self, n_bytes: int = 0) -> bytes:
        try:
            if n_bytes <= 0:
                self.buffer.extend(self.serial.read_all())
                msg = bytes(self.buffer)
                self.buffer = bytearray()
                return msg
            else:
                if len(self.buffer) < n_bytes:
                    self.buffer.extend(self.serial.read(n_bytes - len(self.buffer)))
                if len(self.buffer) < n_bytes:
                    msg = bytes(self.buffer)
                    self.buffer = bytearray()
                else:
                    msg, self.buffer = bytes(self.buffer[:n_bytes]), self.buffer[n_bytes:]
                return msg
        except serial.SerialException as e:
            logger(__name__).debug(e)
            raise PortConnectionException(e)

    def write(self, data: Union[str, bytes]):
        if isinstance(data, str):
            data = data.encode(encoding='ascii')
        self.serial.write(data)

    def flush(self):
        self.serial.flush()

    def destroy(self):
        logger(__name__).debug(f'Destroying {self.__class__.__name__} to {self.serial.name}')
        self.serial.close()

    @property
    def name(self) -> str:
        return self.serial.portstr

    def __str__(self):
        return str(self.serial.port)
