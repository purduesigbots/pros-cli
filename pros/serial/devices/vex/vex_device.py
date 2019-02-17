import struct
import time
from typing import *

from pros.common import *
from pros.serial import bytes_to_str
from pros.serial.ports import BasePort
from . import comm_error
from .message import Message
from ..generic_device import GenericDevice


def debug(msg):
    print(msg)


class VEXDevice(GenericDevice):
    ACK_BYTE = 0x76
    NACK_BYTE = 0xFF

    def __init__(self, port: BasePort, timeout=0.1):
        super().__init__(port)
        self.default_timeout = timeout

    @retries
    def query_system(self) -> bytearray:
        """
        Verify that a VEX device is connected. Returned payload varies by product
        :return: Payload response
        """
        logger(__name__).debug('Sending simple 0x21 command')
        return self._txrx_simple_packet(0x21, 0x0A)

    def _txrx_simple_struct(self, command: int, unpack_fmt: str, timeout: Optional[float] = None) -> Tuple:
        rx = self._txrx_simple_packet(command, struct.calcsize(unpack_fmt), timeout=timeout)
        return struct.unpack(unpack_fmt, rx)

    def _txrx_simple_packet(self, command: int, rx_len: int, timeout: Optional[float] = None) -> bytearray:
        """
        Transmits a simple command to the VEX device, performs the standard quality of message checks, then
        returns the payload.
        Will check if the received command matches the sent command and the received length matches the expected length
        :param command: Command to send to the device
        :param rx_len: Expected length of the received message
        :return: They payload of the message, or raises and exception if there was an issue
        """
        msg = self._txrx_packet(command, timeout=timeout)
        if msg['command'] != command:
            raise comm_error.VEXCommError('Received command does not match sent command.', msg)
        if len(msg['payload']) != rx_len:
            raise comm_error.VEXCommError("Received data doesn't match expected length", msg)
        return msg['payload']

    def _rx_packet(self, timeout: Optional[float] = None) -> Dict[str, Union[Union[int, bytes, bytearray], Any]]:
        # Optimized to read as quickly as possible w/o delay
        start_time = time.time()
        response_header = bytes([0xAA, 0x55])
        response_header_stack = list(response_header)
        rx = bytearray()
        if timeout is None:
            timeout = self.default_timeout
        while (len(rx) > 0 or time.time() - start_time < timeout) and len(response_header_stack) > 0:
            b = self.port.read(1)
            if len(b) == 0:
                continue
            b = b[0]
            if b == response_header_stack[0]:
                response_header_stack.pop(0)
                rx.append(b)
            else:
                logger(__name__).debug("Tossing rx ({}) because {} didn't match".format(bytes_to_str(rx), b))
                response_header_stack = bytearray(response_header)
                rx = bytearray()
        if not rx == bytearray(response_header):
            raise IOError(f"Couldn't find the response header in the device response after {timeout} s. "
                          f"Got {rx.hex()} but was expecting {response_header.hex()}")
        rx.extend(self.port.read(1))
        command = rx[-1]
        rx.extend(self.port.read(1))
        payload_length = rx[-1]
        if command == 0x56 and (payload_length & 0x80) == 0x80:
            logger(__name__).debug('Found an extended message payload')
            rx.extend(self.port.read(1))
            payload_length = ((payload_length & 0x7f) << 8) + rx[-1]
        payload = self.port.read(payload_length)
        rx.extend(payload)
        return {
            'command': command,
            'payload': payload,
            'raw': rx
        }

    def _tx_packet(self, command: int, tx_data: Union[Iterable, bytes, bytearray, None] = None):
        tx = self._form_simple_packet(command)
        if tx_data is not None:
            tx = bytes([*tx, *tx_data])
        logger(__name__).debug(f'{self.__class__.__name__} TX: {bytes_to_str(tx)}')
        self.port.read_all()
        self.port.write(tx)
        self.port.flush()
        return tx

    def _txrx_packet(self, command: int, tx_data: Union[Iterable, bytes, bytearray, None] = None,
                     timeout: Optional[float] = None) -> Message:
        """
        Goes through a send/receive cycle with a VEX device.
        Transmits the command with the optional additional payload, then reads and parses the outer layer
        of the response
        :param command: Command to send the device
        :param tx_data: Optional extra data to send the device
        :return: Returns a dictionary containing the received command field and the payload. Correctly computes the
        payload length even if the extended command (0x56) is used (only applies to the V5).
        """
        tx = self._tx_packet(command, tx_data)
        rx = self._rx_packet(timeout=timeout)
        msg = Message(rx['raw'], tx)
        logger(__name__).debug(msg)
        msg['payload'] = Message(rx['raw'], tx, internal_rx=rx['payload'])
        msg['command'] = rx['command']
        return msg

    @staticmethod
    def _form_simple_packet(msg: int) -> bytearray:
        return bytearray([0xc9, 0x36, 0xb8, 0x47, msg])
