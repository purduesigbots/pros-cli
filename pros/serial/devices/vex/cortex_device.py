import itertools
import time
import typing
from enum import IntFlag
from pathlib import Path
from typing import *

from pros.common import ui
from pros.common.utils import retries, logger
from pros.conductor import Project
from pros.serial import bytes_to_str
from pros.serial.devices.vex import VEXCommError
from pros.serial.devices.vex.stm32_device import STM32Device
from pros.serial.ports import list_all_comports

from .vex_device import VEXDevice
from ..system_device import SystemDevice


def find_cortex_ports():
    return [p for p in list_all_comports() if p.vid is not None and p.vid in [0x4D8, 0x67B]]


class CortexDevice(VEXDevice, SystemDevice):
    class SystemStatus(object):
        def __init__(self, data: Tuple[bytes, ...]):
            self.joystick_firmware = data[0:2]
            self.robot_firmware = data[2:4]
            self.joystick_battery = float(data[4]) * .059
            self.robot_battery = float(data[5]) * .059
            self.backup_battery = float(data[6]) * .059
            self.flags = CortexDevice.SystemStatusFlags(data[7])

        def __str__(self):
            return f'  Tether: {str(self.flags)}\n' \
                   f'  Cortex: F/W {self.robot_firmware[0]}.{self.robot_firmware[1]} w/ {self.robot_battery:1.2f} V ' \
                   f'(Backup: {self.backup_battery:1.2f} V)\n' \
                   f'Joystick: F/W {self.joystick_firmware[0]}.{self.robot_firmware[1]} w/ ' \
                   f'{self.joystick_battery:1.2f} V'

    class SystemStatusFlags(IntFlag):
        DL_MODE = (1 << 0)
        TETH_VN2 = (1 << 2)
        FCS_CONNECT = (1 << 3)
        TETH_USB = (1 << 4)
        DIRECT_USB = (1 << 5)
        FCS_AUTON = (1 << 6)
        FCS_DISABLE = (1 << 7)

        TETH_BITS = DL_MODE | TETH_VN2 | TETH_USB

        def __str__(self):
            def andeq(a, b):
                return (a & b) == b

            if not self.value & self.TETH_BITS:
                s = 'Serial w/VEXnet 1.0 Keys'
            elif andeq(self.value, 0x01):
                s = 'Serial w/VEXnet 1.0 Keys (turbo)'
            elif andeq(self.value, 0x04):
                s = 'Serial w/VEXnet 2.0 Keys'
            elif andeq(self.value, 0x05):
                s = 'Serial w/VEXnet 2.0 Keys (download mode)'
            elif andeq(self.value, 0x10):
                s = 'Serial w/ a USB Cable'
            elif andeq(self.value, 0x20):
                s = 'Directly w/ a USB Cable'
            else:
                s = 'Unknown'

            if andeq(self.value, self.FCS_CONNECT):
                s += ' - FCS Connected'
            return s

    def get_connected_device(self) -> SystemDevice:
        logger(__name__).info('Interrogating Cortex...')
        stm32 = STM32Device(self.port, do_negoitate=False)
        try:
            stm32.get(n_retries=1)
            return stm32
        except VEXCommError:
            return self

    def upload_project(self, project: Project, **kwargs):
        assert project.target == 'cortex'
        output_path = project.path.joinpath(project.output)
        if not output_path.exists():
            raise ui.dont_send(Exception('No output files were found! Have you built your project?'))
        with output_path.open(mode='rb') as pf:
            return self.write_program(pf, **kwargs)

    def write_program(self, file: typing.BinaryIO, **kwargs):
        action_string = ''
        if hasattr(file, 'name'):
            action_string += f' {Path(file.name).name}'
        action_string += f' to Cortex on {self.port}'
        ui.echo(f'Uploading {action_string}')

        logger(__name__).info('Writing program to Cortex')
        status = self.query_system()
        logger(__name__).info(status)
        if not status.flags | self.SystemStatusFlags.TETH_USB and not status.flags | self.SystemStatusFlags.DL_MODE:
            self.send_to_download_channel()

        bootloader = self.expose_bootloader()
        rv = bootloader.write_program(file, **kwargs)

        ui.finalize('upload', f'Finished uploading {action_string}')
        return rv

    @retries
    def query_system(self) -> SystemStatus:
        logger(__name__).info('Querying system information')
        rx = self._txrx_simple_struct(0x21, "<8B2x")
        status = CortexDevice.SystemStatus(rx)
        ui.finalize('cortex-status', status)
        return status

    @retries
    def send_to_download_channel(self):
        logger(__name__).info('Sending to download channel')
        self._txrx_ack_packet(0x35, timeout=1.0)

    @retries
    def expose_bootloader(self):
        logger(__name__).info('Exposing bootloader')
        for _ in itertools.repeat(None, 5):
            self._tx_packet(0x25)
            time.sleep(0.1)
        self.port.read_all()
        time.sleep(0.3)
        return STM32Device(self.port, must_initialize=True)

    def _rx_ack(self, timeout: float = 0.01):
        # Optimized to read as quickly as possible w/o delay
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.port.read(1)[0] == self.ACK_BYTE:
                return
        raise IOError("Device never ACK'd")

    def _txrx_ack_packet(self, command: int, timeout=0.1):
        """
                Goes through a send/receive cycle with a VEX device.
                Transmits the command with the optional additional payload, then reads and parses the outer layer
                of the response
                :param command: Command to send the device
                :param retries: Number of retries to attempt to parse the output before giving up and raising an error
                :return: Returns a dictionary containing the received command field and the payload. Correctly computes
                the payload length even if the extended command (0x56) is used (only applies to the V5).
                """
        tx = self._tx_packet(command)
        self._rx_ack(timeout=timeout)
        logger(__name__).debug('TX: {}'.format(bytes_to_str(tx)))
