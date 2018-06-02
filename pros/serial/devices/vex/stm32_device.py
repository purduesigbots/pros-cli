import itertools
import operator
import struct
import time
import typing
from functools import reduce
from typing import *

import pros.common.ui as ui
from pros.common import logger, retries
from pros.serial import bytes_to_str
from pros.serial.devices.vex import VEXCommError
from pros.serial.ports import BasePort

from ..generic_device import GenericDevice
from ..system_device import SystemDevice


class STM32Device(GenericDevice, SystemDevice):
    ACK_BYTE = 0x79
    NACK_BYTE = 0xFF
    NUM_PAGES = 0xff
    PAGE_SIZE = 0x2000

    def __init__(self, port: BasePort, must_initialize: bool = False, do_negoitate: bool = True):
        super().__init__(port)
        self.commands = bytes([0x00, 0x01, 0x02, 0x11, 0x21, 0x31, 0x43, 0x63, 0x73, 0x82, 0x92])

        if do_negoitate:
            # self.port.write(b'\0' * 255)
            if must_initialize:
                self._txrx_command(0x7f, checksum=False)
            try:
                self.get(n_retries=0)
            except:
                logger(__name__).info('Sending bootloader initialization')
                time.sleep(0.01)
                self.port.rts = 0
                for _ in itertools.repeat(None, times=3):
                    time.sleep(0.01)
                    self._txrx_command(0x7f, checksum=False)
                    time.sleep(0.01)
                    self.get()

    def write_program(self, file: typing.BinaryIO, preserve_fs: bool = False, go_after: bool = True, **_):
        file_len = file.seek(0, 2)
        file.seek(0, 0)
        if file_len > (self.NUM_PAGES * self.PAGE_SIZE):
            raise VEXCommError(
                f'File is too big to be uploaded (max file size: {self.NUM_PAGES * self.PAGE_SIZE} bytes)')

        if hasattr(file, 'name'):
            display_name = file.name
        else:
            display_name = '(memory)'

        if not preserve_fs:
            self.erase_all()
        else:
            self.erase_memory(list(range(0, int(file_len / self.PAGE_SIZE) + 1)))

        address = 0x08000000
        with ui.progressbar(length=file_len, label=f'Uploading {display_name}') as progress:
            for i in range(0, file_len, 256):
                write_size = 256
                if i + 256 > file_len:
                    write_size = file_len - i
                self.write_memory(address, file.read(write_size))
                address += write_size
                progress.update(write_size)

        if go_after:
            self.go(0x08000000)

    def scan_prosfs(self):
        pass

    @retries
    def get(self):
        logger(__name__).info('STM32: Get')
        self._txrx_command(0x00)
        n_bytes = self.port.read(1)[0]
        assert n_bytes == 11
        data = self.port.read(n_bytes + 1)
        logger(__name__).info(f'STM32 Bootloader version 0x{data[0]:x}')
        self.commands = data[1:]
        logger(__name__).debug(f'STM32 Bootloader commands are: {bytes_to_str(data[1:])}')
        assert self.port.read(1)[0] == self.ACK_BYTE

    @retries
    def get_read_protection_status(self):
        logger(__name__).info('STM32: Get ID & Read Protection Status')
        self._txrx_command(0x01)
        data = self.port.read(3)
        logger(__name__).debug(f'STM32 Bootloader Get Version & Read Protection Status is: {bytes_to_str(data)}')
        assert self.port.read(1)[0] == self.ACK_BYTE

    @retries
    def get_id(self):
        logger(__name__).info('STM32: Get PID')
        self._txrx_command(0x02)
        n_bytes = self.port.read(1)[0]
        pid = self.port.read(n_bytes + 1)
        logger(__name__).debug(f'STM32 Bootloader PID is {pid}')

    @retries
    def read_memory(self, address: int, n_bytes: int):
        logger(__name__).info(f'STM32: Read {n_bytes} fromo 0x{address:x}')
        assert 255 >= n_bytes > 0
        self._txrx_command(0x11)
        self._txrx_command(struct.pack('>I', address))
        self._txrx_command(n_bytes)
        return self.port.read(n_bytes)

    @retries
    def go(self, start_address: int):
        logger(__name__).info(f'STM32: Go 0x{start_address:x}')
        self._txrx_command(0x21)
        try:
            self._txrx_command(struct.pack('>I', start_address), timeout=5.)
        except VEXCommError:
            logger(__name__).warning('STM32 Bootloader did not acknowledge GO command. '
                                     'The program may take a moment to begin running '
                                     'or the device should be rebooted.')

    @retries
    def write_memory(self, start_address: int, data: bytes):
        logger(__name__).info(f'STM32: Write {len(data)} to 0x{start_address:x}')
        assert 0 < len(data) <= 256
        if len(data) % 4 != 0:
            data = data + (b'\0' * (4 - (len(data) % 4)))
        self._txrx_command(0x31)
        self._txrx_command(struct.pack('>I', start_address))
        self._txrx_command(bytes([len(data) - 1, *data]))

    @retries
    def erase_all(self):
        logger(__name__).info('STM32: Erase all pages')
        if not self.commands[6] == 0x43:
            raise VEXCommError('Standard erase not supported on this device (only extended erase)')
        self._txrx_command(0x43)
        self._txrx_command(0xff)

    @retries
    def erase_memory(self, page_numbers: List[int]):
        logger(__name__).info(f'STM32: Erase pages: {page_numbers}')
        if not self.commands[6] == 0x43:
            raise VEXCommError('Standard erase not supported on this device (only extended erase)')
        assert 0 < len(page_numbers) <= 255
        assert all([0 <= p <= 255 for p in page_numbers])
        self._txrx_command(0x43)
        self._txrx_command(bytes([len(page_numbers) - 1, *page_numbers]))

    @retries
    def extended_erase(self, page_numbers: List[int]):
        logger(__name__).info(f'STM32: Extended Erase pages: {page_numbers}')
        if not self.commands[6] == 0x44:
            raise IOError('Extended erase not supported on this device (only standard erase)')
        assert 0 < len(page_numbers) < 0xfff0
        assert all([0 <= p <= 0xffff for p in page_numbers])
        self._txrx_command(0x44)
        self._txrx_command(bytes([len(page_numbers) - 1, *struct.pack(f'>{len(page_numbers)}H', *page_numbers)]))

    @retries
    def extended_erase_special(self, command: int):
        logger(__name__).info(f'STM32: Extended special erase: {command:x}')
        if not self.commands[6] == 0x44:
            raise IOError('Extended erase not supported on this device (only standard erase)')
        assert 0xfffd <= command <= 0xffff
        self._txrx_command(0x44)
        self._txrx_command(struct.pack('>H', command))

    def _txrx_command(self, command: Union[int, bytes], timeout: float = 0.01, checksum: bool = True):
        self.port.read_all()
        if isinstance(command, bytes):
            message = command + (bytes([reduce(operator.xor, command, 0x00)]) if checksum else bytes([]))
        elif isinstance(command, int):
            message = bytearray([command, ~command & 0xff] if checksum else [command])
        else:
            raise ValueError(f'Expected command to be bytes or int but got {type(command)}')
        logger(__name__).debug(f'STM32 TX: {bytes_to_str(message)}')
        self.port.write(message)
        self.port.flush()
        start_time = time.time()
        while time.time() - start_time < timeout:
            data = self.port.read(1)
            if data and len(data) == 1:
                logger(__name__).debug(f'STM32 RX: {data[0]} =?= {self.ACK_BYTE}')
                if data[0] == self.ACK_BYTE:
                    return
        raise VEXCommError(f"Device never ACK'd to {command}", command)
