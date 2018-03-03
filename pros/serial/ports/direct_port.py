from typing import *

import serial
from cobs import cobs

from .base_port import BasePort

from pros.common import logger
import binascii

def create_serial_port(port_name: str, timeout: Optional[float] = 1.0) -> serial.Serial:
    port = serial.Serial(port_name, baudrate=115200, bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    port.timeout = timeout
    port.inter_byte_timeout = 0.2
    return port


class DirectPort(BasePort):
    def __init__(self, port_name: str, **kwargs):
        self.serial: serial.Serial = create_serial_port(port_name=port_name, timeout=kwargs.pop('timeout', 1.0))
        self._config: Dict[str, Any] = {}
        self.buffer: Union[bytearray, List[Tuple[bytes, bytes]]] = None
        self.temp_buffer: bytearray = None
        self.decoder: Callable[int, Union[bytes, Tuple[bytes, bytes]]] = None
        for (key, value) in kwargs.items():
            self.config(key, value)
        if 'cobs' not in self._config:
            self.config('cobs', False)

    def _cobs_read(self, n_bytes: int = -1) -> Tuple[bytes, bytes]:
        assert isinstance(self.buffer, list)
        if len(self.buffer) == 0:
            if b'\0' not in self.temp_buffer:
                self.temp_buffer.extend(self.serial.read(1))
                self.temp_buffer.extend(self.serial.read(-1))
            if b'\0' in self.temp_buffer:
                msg, self.temp_buffer = self.temp_buffer.split(b'\0', 1)
                try:
                    msg = cobs.decode(msg)
                except cobs.DecodeError:
                    logger(__name__).warning(f'Could not decode bytes: {msg.hex()}')
                self.buffer.append((msg[:4], msg[4:]))
        return self.buffer.pop(0) if len(self.buffer) > 0 else (b'', b'')

    def _raw_read(self, n_bytes: int = 0) -> Tuple[bytes, bytes]:
        assert isinstance(self.buffer, bytearray)
        if n_bytes == 0:
            self.buffer.extend(self.serial.read_all())
            msg = bytes(self.buffer)
            self.buffer = bytearray()
            return b'', msg
        else:
            if len(self.buffer) < n_bytes:
                self.buffer.extend(self.serial.read(n_bytes - len(self.buffer)))
            msg = bytes(self.buffer[:n_bytes])
            self.buffer = self.buffer[n_bytes:]
            return (b'', msg) if len(msg) > 0 else (b'', b'')

    def read(self, n_bytes: int = 0) -> Tuple[bytes, bytes]:
        return self.decoder(n_bytes)

    def write(self, data: Union[str, bytes]):
        if isinstance(data, str):
            data = data.encode(encoding='ascii')
        self.serial.write(data)

    def config(self, command: str, argument: Any):
        if command == 'cobs':
            new_cobs = bool(argument)
            if new_cobs != self._config.get('cobs', None):
                if new_cobs:  # moving to cobs encoding
                    self.temp_buffer = bytearray()
                    self.buffer = []
                    self.decoder = self._cobs_read
                else:  # moving to raw encoding
                    self.buffer = bytearray()
                    self.decoder = self._raw_read
            self._config['cobs'] = new_cobs

    def flush_input(self):
        if self._config['cobs']:
            self.temp_buffer = bytearray()
            self.buffer = []
        else:
            self.buffer = bytearray()

    def flush_output(self):
        self.serial.flush()
