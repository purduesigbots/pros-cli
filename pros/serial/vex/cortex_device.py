import time
from enum import Flag
from typing import *

from .vex_device import VEXDevice
from .. import bytes_to_str
from pros.common.utils import retries

from pros.serial.ports import list_all_comports


def find_cortex_ports():
    return [p for p in list_all_comports() if p.vid is not None and p.vid in [0x4D8, 0x67B]]


class CortexDevice(VEXDevice):
    class SystemStatus(Flag):
        DL_MODE = (1 << 0)
        TETH_VN2 = (1 << 2)
        FCS_CONNECT = (1 << 3)
        TETH_USB = (1 << 4)
        DIRECT_USB = (1 << 5)
        FCS_AUTON = (1 << 6)
        FCS_DISABLE = (1 << 7)

    @retries
    def query_system(self) -> Dict[str, Any]:
        rx = self._txrx_simple_struct(0x21, "<8B2x")
        return {
            'joystick_firmware': rx[0:2],
            'robot_firmware': rx[2:4],
            'joystick_battery': float(rx[4]) * .059,
            'robot_battery': float(rx[5]) * .059,
            'backup_batter': float(rx[6]) * .059,
            'status': self.SystemStatus(rx[7])
        }

    @retries
    def send_to_download_channel(self):
        self._txrx_ack_packet(0x35, timeout=1.0)

    @retries
    def expose_bootloader(self):
        self._txrx_ack_packet(0x25, timeout=1.0)

    def _rx_ack(self, timeout: float = 0.01):
        # Optimized to read as quickly as possible w/o delay
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.port.read(1)[0] == self.ACK_BYTE:
                return
        raise IOError("Device never ACK'd")

    def _txrx_ack_packet(self, command: int, retries: int = 10, timeout=0.1):
        """
                Goes through a send/receive cycle with a VEX device.
                Transmits the command with the optional additional payload, then reads and parses the outer layer
                of the response
                :param command: Command to send the device
                :param retries: Number of retries to attempt to parse the output before giving up and raising an error
                :return: Returns a dictionary containing the received command field and the payload. Correctly computes the
                payload length even if the extended command (0x56) is used (only applies to the V5).
                """
        try:
            tx = self._tx_packet(command)
            self._rx_ack(timeout=timeout)
            self.debug_print('TX: {}'.format(bytes_to_str(tx)))
            return None, retries
        except BaseException as e:
            if retries > 0:
                return self._txrx_packet(command, retries=retries - 1)
            else:
                raise e
