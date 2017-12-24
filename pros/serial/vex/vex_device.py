from serial import Serial
import time
from typing import *
import struct
from .. import bytes_to_str


def decode_bytes_to_str(data: Union[bytes, bytearray], encoding: str='utf-8') -> str:
    return data.split(b'\0', 1)[0].decode(encoding=encoding)


def debug(msg):
    print(msg)


class VexDevice(object):
    ACK_BYTE = 0x76
    NACK_BYTE = 0xFF

    def __init__(self, port: Serial, debug_print: Callable[[str], None]=debug):
        self.port = port
        if not self.port.is_open:
            self.port.open()
        self.debug_print = debug_print

    def query_system(self, retries=10) -> bytearray:
        """
        Verify that a VEX device is connected. Returned payload varies by product
        :param retries: Number of retries to attempt to parse the output before giving up and raising an error
        :return: Payload response
        """
        return self._txrx_simple_packet(0x21, 0x0A, retries=retries)

    def _txrx_simple_struct(self, command: int, unpack_fmt: str,
                            retries: int=5) -> Tuple:
        rx = self._txrx_simple_packet(command, struct.calcsize(unpack_fmt), retries=retries)
        return struct.unpack(unpack_fmt, rx)

    def _txrx_simple_packet(self, command: int, rx_len: int,
                            retries: int=5) -> bytearray:
        """
        Transmits a simple command to the VEX device, performs the standard quality of message checks, then
        returns the payload.
        Will check if the received command matches the sent command and the received length matches the expected length
        :param command: Command to send to the device
        :param rx_len: Expected length of the received message
        :param retries: Number of retries to attempt to parse the output before giving up and raising an error
        :return: They payload of the message, or raises and exception if there was an issue
        """
        try:
            rx, _ = self._txrx_packet(command, retries=retries)
            assert(rx['command'] == command)
            assert(len(rx['payload']) == rx_len)
            return rx['payload']
        except BaseException as e:
            if retries > 0:
                return self._txrx_simple_packet(command, rx_len, retries=retries-1)
            else:
                raise e

    def _rx_packet(self, timeout: float=0.01) -> Dict[str, Any]:
        # Optimized to read as quickly as possible w/o delay
        start_time = time.time()
        response_header = bytes([0xAA, 0x55])
        response_header_stack = list(response_header)
        rx = bytearray()
        while (len(rx) > 0 or time.time() - start_time < timeout) and len(response_header_stack) > 0:
            b = self.port.read(1)[0]
            if b == response_header_stack[0]:
                response_header_stack.pop(0)
                rx.append(b)
            else:
                response_header_stack = bytearray(response_header)
                rx = bytearray()
        if not rx == bytearray(response_header):
            raise IOError("Couldn't find the response header in the device response")
        rx.extend(self.port.read(1))
        command = rx[-1]
        rx.extend(self.port.read(1))
        payload_length = rx[-1]
        if command == 0x56 and (payload_length & 0x80) == 0x80:
            rx.extend(self.port.read(1))
            payload_length = ((payload_length & 0x7f) << 8) + rx[-1]
        payload = self.port.read(payload_length)
        rx.extend(payload)
        recv = {
            'command': command,
            'payload': payload,
            'raw': rx
        }
        return recv

    def _tx_packet(self, command: int, tx_data: Union[Iterable, bytes, bytearray, None]=None):
        tx = self._form_simple_packet(command)
        if tx_data is not None:
            tx = bytes([*tx, *tx_data])
        self.port.read_all()
        self.port.write(tx)
        self.port.flush()
        return tx

    def _txrx_packet(self, command: int,
                     tx_data: Union[Iterable, bytes, bytearray, None] = None,
                     retries: int=5) -> Tuple[Dict[str, Any], int]:
        """
        Goes through a send/receive cycle with a VEX device.
        Transmits the command with the optional additional payload, then reads and parses the outer layer
        of the response
        :param command: Command to send the device
        :param tx_data: Optional extra data to send the device
        :param retries: Number of retries to attempt to parse the output before giving up and raising an error
        :return: Returns a dictionary containing the received command field and the payload. Correctly computes the
        payload length even if the extended command (0x56) is used (only applies to the V5).
        """
        try:
            tx = self._tx_packet(command, tx_data)
            recv = self._rx_packet()
            self.debug_print('TX: {}'.format(bytes_to_str(tx)))
            self.debug_print('RX: {}'.format(bytes_to_str(recv['raw'])))
            return recv, retries
        except BaseException as e:
            if retries > 0:
                return self._txrx_packet(command, tx_data=tx_data, retries=retries - 1)
            else:
                raise e

    @staticmethod
    def _form_simple_packet(msg: int) -> bytearray:
        return bytearray([0xc9, 0x36, 0xb8, 0x47, msg])

