import gzip
import io
import re
import struct
import typing
from configparser import ConfigParser
from datetime import datetime, timedelta
from enum import IntEnum
from io import BytesIO, StringIO
from typing import *

from semantic_version import Spec

from pros.common import *
from pros.serial import bytes_to_str, decode_bytes_to_str
from pros.serial.ports import BasePort, list_all_comports
from .comm_error import VEXCommError
from .crc import CRC
from .message import Message
from .vex_device import VEXDevice
from ..system_device import SystemDevice

int_str = Union[int, str]


def find_v5_ports(p_type: str):
    def filter_vex_ports(p):
        return p.vid is not None and p.vid in [0x2888, 0x0501] or \
               p.name is not None and ('VEX' in p.name or 'V5' in p.name)

    def filter_v5_ports(p, locations, names):
        return (p.location is not None and any([p.location.endswith(l) for l in locations])) or \
               (p.name is not None and any([n in p.name for n in names])) or \
               (p.description is not None and any([n in p.description for n in names]))

    ports = [p for p in list_all_comports() if filter_vex_ports(p)]

    # Initially try filtering based off of location or the name of the device.
    # Doesn't work on macOS or Jonathan's Dell, so we have a fallback (below)
    user_ports = [p for p in ports if filter_v5_ports(p, ['2'], ['User'])]
    system_ports = [p for p in ports if filter_v5_ports(p, ['0'], ['System', 'Communications'])]
    joystick_ports = []  # joystick comms are very slow/unusable
    # joystick_ports = [p for p in ports if filter_v5_ports(p, ['1'], ['Controller'])]

    # TODO: test this code path (hard)
    if len(user_ports) != len(system_ports):
        if len(user_ports) > len(system_ports):
            user_ports = [p for p in user_ports if p not in system_ports]
        else:
            system_ports = [p for p in system_ports if p not in user_ports]

    if len(user_ports) == len(system_ports) and len(user_ports) > 0:
        if p_type.lower() == 'user':
            return user_ports
        elif p_type.lower() == 'system':
            return system_ports
        else:
            raise ValueError(f'Invalid port type specified: {p_type}')

    # None of the typical filters worked, so if there are only two ports, then the lower one is always*
    # the USER? port (*always = I haven't found a guarantee)
    if len(ports) == 2:
        # natural sort based on: https://stackoverflow.com/a/16090640
        def natural_key(chunk: str):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', chunk)]

        ports = sorted(ports, key=lambda p: natural_key(p.device))
        if p_type.lower() == 'user':
            return [ports[1]]
        elif p_type.lower() == 'system':
            return [ports[0]]
        else:
            raise ValueError(f'Invalid port type specified: {p_type}')
    if len(joystick_ports) > 0:
        return joystick_ports
    return []


class V5Device(VEXDevice, SystemDevice):
    vid_map = {'user': 1, 'system': 15}  # type: Dict[str, int]

    class FTCompleteOptions(IntEnum):
        DONT_RUN = 0
        RUN_IMMEDIATELY = 0b01
        RUN_SCREEN = 0b11

    VEX_CRC16 = CRC(16, 0x1021)  # CRC-16-CCIT
    VEX_CRC32 = CRC(32, 0x04C11DB7)  # CRC-32 (the one used everywhere but has no name)

    def __init__(self, port: BasePort):
        self._status = None
        super().__init__(port)

    @property
    def status(self):
        if not self._status:
            self._status = self.get_system_status()
        return self._status

    def generate_ini_file(self, remote_name: str = None, slot: int = 0, ini: ConfigParser = None, **kwargs):
        project_ini = ConfigParser()
        from semantic_version import Spec
        default_icon = 'USER902x.bmp' if Spec('>=1.0.0-22').match(self.status['cpu0_version']) else 'USER999x.bmp'
        project_ini['program'] = {
            'version': kwargs.get('version', '0.0.0') or '0.0.0',
            'name': remote_name,
            'slot': slot,
            'icon': kwargs.get('icon', default_icon) or default_icon,
            'description': kwargs.get('description', 'Created with PROS'),
            'date': datetime.now().isoformat()
        }
        if ini:
            project_ini.update(ini)
        with StringIO() as ini_str:
            project_ini.write(ini_str)
            logger(__name__).info(f'Created ini: {ini_str.getvalue()}')
            return ini_str.getvalue()

    def write_program(self, file: typing.BinaryIO, remote_name: str = None, ini: ConfigParser = None, slot: int = 0,
                      file_len: int = -1, run_after: FTCompleteOptions = FTCompleteOptions.DONT_RUN,
                      target: str = 'flash', quirk: int = 0, compress_bin: bool = True, **kwargs):
        remote_base = f'slot_{slot + 1}'
        if target == 'ddr':
            self.write_file(file, f'{remote_base}.bin', file_len=file_len, type='bin',
                            target='ddr', run_after=run_after, **kwargs)
            return
        if not isinstance(ini, ConfigParser):
            ini = ConfigParser()
        if not remote_name:
            remote_name = file.name
        if len(remote_name) > 20:
            logger(__name__).info('Truncating remote name to {} for length.'.format(remote_name[:20]))
            remote_name = remote_name[:20]

        ini_file = self.generate_ini_file(remote_name=remote_name, slot=slot, ini=ini, **kwargs)
        logger(__name__).info(f'Created ini: {ini_file}')

        if (quirk & 0xff) == 1:
            # WRITE BIN FILE
            self.write_file(file, f'{remote_base}.bin', file_len=file_len, type='bin', run_after=run_after,
                            compress=compress_bin, **kwargs)
            with BytesIO(ini_file.encode(encoding='ascii')) as ini_bin:
                # WRITE INI FILE
                self.write_file(ini_bin, f'{remote_base}.ini', type='ini', **kwargs)
        elif (quirk & 0xff) == 0:
            # STOP PROGRAM
            self.execute_program_file('', run=False)
            with BytesIO(ini_file.encode(encoding='ascii')) as ini_bin:
                # WRITE INI FILE
                self.write_file(ini_bin, f'{remote_base}.ini', type='ini', **kwargs)
            # WRITE BIN FILE
            self.write_file(file, f'{remote_base}.bin', file_len=file_len, type='bin', run_after=run_after,
                            compress=compress_bin, **kwargs)
        else:
            raise ValueError(f'Unknown quirk option: {quirk}')

    def read_file(self, file: typing.IO[bytes], remote_file: str, vid: int_str = 'user', target: int_str = 'flash',
                  addr: Optional[int] = None, file_len: Optional[int] = None):
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        if addr is None:
            metadata = self.get_file_metadata_by_name(remote_file, vid=vid)
            addr = metadata['addr']
        ft_meta = self.ft_initialize(remote_file, function='download', vid=vid, target=target)
        if file_len is None:
            file_len = ft_meta['file_size']
        with ui.progressbar(length=file_len, label='Downloading {}'.format(remote_file)) as progress:
            for i in range(0, file_len, ft_meta['max_packet_size']):
                packet_size = ft_meta['max_packet_size']
                if i + ft_meta['max_packet_size'] > file_len:
                    packet_size = ft_meta['file_size'] - i
                file.write(self.ft_read(addr + i, packet_size))
                progress.update(packet_size)
                logger(__name__).debug('Completed {} of {} bytes'.format(i + packet_size, file_len))
        self.ft_complete()

    def write_file(self, file: typing.BinaryIO, remote_file: str, file_len: int = -1,
                   run_after: FTCompleteOptions = FTCompleteOptions.DONT_RUN, compress: bool = False, **kwargs):
        if file_len < 0:
            file_len = file.seek(0, 2)
            file.seek(0, 0)
        if compress and self.status['system_version'] in Spec('>=1.0.5'):
            buf = io.BytesIO()
            with ui.progressbar(length=file_len, label='Compressing binary') as progress:
                with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                    while True:
                        data = file.read(16 * 1024)
                        if not data:
                            break
                        f.write(data)
                        progress.update(len(data))
            file = buf
            # recompute file length
            file_len = file.seek(0, 2)
            file.seek(0, 0)

        crc32 = self.VEX_CRC32.compute(file.read(file_len))
        file.seek(-file_len, 2)
        addr = kwargs.get('addr', 0x03800000)
        logger(__name__).info('Transferring {} ({} bytes) to the V5 from {}'.format(remote_file, file_len, file))
        ft_meta = self.ft_initialize(remote_file, function='upload', length=file_len, crc=crc32, **kwargs)
        assert ft_meta['file_size'] >= file_len
        if len(remote_file) > 24:
            logger(__name__).info('Truncating {} to {} due to length'.format(remote_file, remote_file[:24]))
            remote_file = remote_file[:24]
        display_name = remote_file
        if hasattr(file, 'name'):
            display_name = '{} ({})'.format(remote_file, file.name)
        max_packet_size = int(ft_meta['max_packet_size'] / 2)
        with ui.progressbar(length=file_len, label='Uploading {}'.format(display_name)) as progress:
            for i in range(0, file_len, max_packet_size):
                packet_size = max_packet_size
                if i + max_packet_size > file_len:
                    packet_size = file_len - i
                logger(__name__).debug('Writing {} bytes at 0x{:02X}'.format(packet_size, addr + i))
                self.ft_write(addr + i, file.read(packet_size))
                progress.update(packet_size)
                logger(__name__).debug('Completed {} of {} bytes'.format(i + packet_size, file_len))
        logger(__name__).debug('Data transfer complete, sending ft complete')
        if compress and self.status['system_version'] in Spec('>=1.0.5'):
            logger(__name__).info('Closing gzip file')
            file.close()
        self.ft_complete(options=run_after)

    def capture_screen(self) -> Tuple[List[List[int]], int, int]:
        self.sc_init()
        width, height = 512, 272
        file_size = width * height * 4  # ARGB

        rx_io = BytesIO()
        self.read_file(rx_io, '', vid='system', target='screen', addr=0, file_len=file_size)
        rx = rx_io.getvalue()

        data = [[] for _ in range(height)]
        for y in range(height):
            for x in range(width - 1):
                if x < 480:
                    px = rx[y * width + x]
                    data[y].append((px & 0xff0000) >> 16)
                    data[y].append((px & 0x00ff00) >> 8)
                    data[y].append(px & 0x0000ff)

        return data, 480, height

    @retries
    def query_system_version(self) -> bytearray:
        logger(__name__).debug('Sending simple 0xA4 command')
        ret = self._txrx_simple_packet(0xA4, 0x08)
        logger(__name__).debug('Completed simple 0xA4 command')
        return ret

    @retries
    def ft_initialize(self, file_name: str, **kwargs) -> Dict[str, Any]:
        logger(__name__).debug('Sending ext 0x11 command')
        options = {
            'function': 'upload',
            'target': 'flash',
            'vid': 'user',
            'overwrite': True,
            'options': 0,
            'length': 0,
            'addr': 0x03800000,
            'crc': 0,
            'type': 'pros',
            'timestamp': datetime.now(),
            'version': 0x01_00_00_00,
            'name': file_name
        }
        options.update({k: v for k, v in kwargs.items() if k in options})

        if isinstance(options['function'], str):
            options['function'] = {'upload': 1, 'download': 2}[options['function'].lower()]
        if isinstance(options['target'], str):
            options['target'] = {'ddr': 0, 'flash': 1, 'screen': 2}[options['target'].lower()]
        if isinstance(options['vid'], str):
            options['vid'] = self.vid_map[options['vid'].lower()]
        if isinstance(options['type'], str):
            options['type'] = options['type'].encode(encoding='ascii')
        options['options'] |= 1 if options['overwrite'] else 0
        options['timestamp'] = int((options['timestamp'] - datetime(2000, 1, 1)).total_seconds())

        logger(__name__).debug('Initializing file transfer w/: {}'.format(options))
        tx_payload = struct.pack("<4B3I4s2I24s", options['function'], options['target'], options['vid'],
                                 options['options'], options['length'], options['addr'], options['crc'],
                                 options['type'], options['timestamp'], options['version'],
                                 options['name'].encode(encoding='ascii'))
        rx = self._txrx_ext_struct(0x11, tx_payload, "<H2I")
        rx = dict(zip(['max_packet_size', 'file_size', 'crc'], rx))
        logger(__name__).debug('response: {}'.format(rx))
        logger(__name__).debug('Completed ext 0x11 command')
        return rx

    @retries
    def ft_complete(self, options: FTCompleteOptions = FTCompleteOptions.DONT_RUN):
        logger(__name__).debug('Sending ext 0x12 command')
        if isinstance(options, bool):
            options = self.FTCompleteOptions.RUN_IMMEDIATELY if options else self.FTCompleteOptions.DONT_RUN
        tx_payload = struct.pack("<B", options.value)
        ret = self._txrx_ext_packet(0x12, tx_payload, 0, timeout=5.0)
        logger(__name__).debug('Completed ext 0x12 command')
        return ret

    @retries
    def ft_write(self, addr: int, payload: Union[Iterable, bytes, bytearray, str]):
        logger(__name__).debug('Sending ext 0x13 command')
        if isinstance(payload, str):
            payload = payload.encode(encoding='ascii')
        if len(payload) % 4 != 0:
            padded_payload = bytes([*payload, *([0] * (4 - (len(payload) % 4)))])
        else:
            padded_payload = payload
        tx_fmt = "<I{}s".format(len(padded_payload))
        tx_payload = struct.pack(tx_fmt, addr, padded_payload)
        ret = self._txrx_ext_packet(0x13, tx_payload, 0)
        logger(__name__).debug('Completed ext 0x13 command')
        return ret

    @retries
    def ft_read(self, addr: int, n_bytes: int) -> bytearray:
        logger(__name__).debug('Sending ext 0x14 command')
        req_n_bytes = n_bytes + ((4 - (n_bytes % 4)) if n_bytes % 4 != 0 else 0)
        tx_payload = struct.pack("<IH", addr, req_n_bytes)
        rx_fmt = "<I{}s{}s".format(n_bytes, ((4 - (n_bytes % 4)) if n_bytes % 4 != 0 else 0))
        ret = self._txrx_ext_struct(0x14, tx_payload, rx_fmt, check_ack=False,
                                    check_length=False)[1]
        logger(__name__).debug('Completed ext 0x14 command')
        return ret[:-1]

    @retries
    def ft_set_link(self, link_name: str, vid: int_str = 'user', options: int = 0):
        logger(__name__).debug('Sending ext 0x15 command')
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]

        tx_payload = struct.pack("<2I24s", vid, options, link_name)
        ret = self._txrx_ext_packet(0x15, tx_payload, 0)
        logger(__name__).debug('Completed ext 0x15 command')
        return ret

    @retries
    def get_dir_count(self, vid: int_str = 1, options: int = 0) \
            -> int:
        logger(__name__).debug('Sending ext 0x16 command')
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        tx_payload = struct.pack("<2B", vid, options)
        ret = self._txrx_ext_struct(0x16, tx_payload, "<h")[0]
        logger(__name__).debug('Completed ext 0x16 command')
        return ret

    @retries
    def get_file_metadata_by_idx(self, file_idx: int, options: int = 0) \
            -> Dict[str, Any]:
        logger(__name__).debug('Sending ext 0x17 command')
        tx_payload = struct.pack("<2B", file_idx, options)
        rx = self._txrx_ext_struct(0x17, tx_payload, "<B3l4sll24s")
        rx = dict(zip(['idx', 'size', 'addr', 'crc', 'type', 'timestamp', 'version', 'filename'], rx))
        rx['type'] = decode_bytes_to_str(rx['type'])
        rx['timestamp'] = datetime(2000, 1, 1) + timedelta(seconds=rx['timestamp'])
        rx['filename'] = decode_bytes_to_str(rx['filename'])
        logger(__name__).debug('Completed ext 0x17 command')
        return rx

    @retries
    def execute_program_file(self, file_name: str, vid: int_str = 'user', run: bool = True):
        logger(__name__).debug('Sending ext 0x18 command')
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        options = 0
        options |= (0 if run else 0x80)
        logger(__name__).debug('VID: {}\tOptions: {}\tFile name: {}'.format(vid, options, file_name))
        tx_payload = struct.pack("<2B24s", vid, options, file_name.encode(encoding='ascii'))
        ret = self._txrx_ext_packet(0x18, tx_payload, 0)
        logger(__name__).debug('Completed ext 0x18 command')
        return ret

    @retries
    def get_file_metadata_by_name(self, file_name: str, vid: int_str = 1, options: int = 0) \
            -> Dict[str, Any]:
        logger(__name__).debug('Sending ext 0x19 command')
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        tx_payload = struct.pack("<2B24s", vid, options, file_name.encode(encoding='ascii'))
        rx = self._txrx_ext_struct(0x19, tx_payload, "<x3l4sll24s")
        rx = dict(zip(['size', 'addr', 'crc', 'type', 'timestamp', 'version', 'linked_filename'], rx))
        rx['type'] = decode_bytes_to_str(rx['type'])
        rx['timestamp'] = datetime(2000, 1, 1) + timedelta(seconds=rx['timestamp'])
        rx['linked_filename'] = decode_bytes_to_str(rx['linked_filename'])
        logger(__name__).debug('Completed ext 0x19 command')
        return rx

    @retries
    def set_program_file_metadata(self, file_name: str, **kwargs):
        logger(__name__).debug('Sending ext 0x1A command')
        options = {
            'vid': 'user',
            'options': 0,
            'addr': -1,
            'type': -1,
            'timestamp': -1,
            'version': -1
        }  # Dict[str, Any]
        options.update(**kwargs)
        if isinstance(options['vid'], str):
            options['vid'] = self.vid_map[options['vid'].lower()]
        if isinstance(options['timestamp'], datetime):
            assert (isinstance(options['timestamp'], datetime))
            options['timestamp'] = (options['timestamp'] - datetime(2000, 1, 1)).get_seconds()
        if isinstance(options['type'], str):
            options['type'] = options['type'].encode(encoding='ascii')
        tx_payload = struct.pack("<2BI4s2I24s", options['vid'], options['options'],
                                 options['addr'], options['type'], options['timestamp'],
                                 options['version'], file_name.encode(encoding='ascii'))
        ret = self._txrx_ext_packet(0x1A, tx_payload, 0)
        logger(__name__).debug('Completed ext 0x1A command')
        return ret

    @retries
    def erase_file(self, file_name: str, erase_all: bool = False, vid: int_str = 'user'):
        logger(__name__).debug('Sending ext 0x1B command')
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        options = 0
        options |= (0x80 if erase_all else 0)
        tx_payload = struct.pack('<2B24s', vid, options, file_name.encode(encoding='ascii'))
        recv = self._txrx_ext_packet(0x1B, tx_payload, 0)
        self.ft_complete()
        logger(__name__).debug('Completed ext 0x1B command')
        return recv

    @retries
    def get_program_file_slot(self, file_name: str, vid: int = 1, options: int = 0) \
            -> Dict[str, Any]:
        logger(__name__).debug('Sending ext 0x1C command')
        tx_payload = struct.pack("<2B24s", vid, options, file_name.encode(encoding='ascii'))
        ret = self._txrx_ext_struct(0x1C, tx_payload, "<B")[0]
        logger(__name__).debug('Completed ext 0x1C command')
        return ret

    @retries
    def get_device_status(self):
        raise NotImplementedError()

    @retries
    def get_system_status(self) -> Dict[str, Any]:
        logger(__name__).debug('Sending ext 0x22 command')
        rx = self._txrx_ext_struct(0x22, [], "<x12B3xBI12x")
        logger(__name__).debug('Completed ext 0x22 command')
        from semantic_version import Version
        return {
            'system_version': Version('{}.{}.{}-{}'.format(*rx[0:4])),
            'cpu0_version': Version('{}.{}.{}-{}'.format(*rx[4:8])),
            'cpu1_version': Version('{}.{}.{}-{}'.format(*rx[8:12])),
            'touch_version': rx[12],
            'system_id': rx[13]
        }

    @retries
    def sc_init(self) -> None:
        """
        Send command to initialize screen capture
        """
        # This will only copy data in memory, not send!
        logger(__name__).debug('Sending ext 0x28 command')
        self._txrx_ext_struct(0x28, [], '')
        logger(__name__).debug('Completed ext 0x28 command')

    def _txrx_ext_struct(self, command: int, tx_data: Union[Iterable, bytes, bytearray],
                         unpack_fmt: str, check_length: bool = True, check_ack: bool = True,
                         timeout: float = 0.1) -> Tuple:
        """
        Transmits and receives an extended command to the V5, automatically unpacking the values according to unpack_fmt
        which gets passed into struct.unpack. The size of the payload is determined from the fmt string
        :param command: Extended command code
        :param tx_data: Transmission payload
        :param unpack_fmt: Format to expect the raw payload to be in
        :param retries: Number of retries to attempt to parse the output before giving up
        :param rx_wait: Amount of time to wait after transmitting the packet before reading the response
        :param check_ack: If true, then checks the first byte of the extended payload as an AK byte
        :return: A tuple unpacked according to the unpack_fmt
        """
        rx = self._txrx_ext_packet(command, tx_data, struct.calcsize(unpack_fmt),
                                   check_length=check_length, check_ack=check_ack, timeout=timeout)
        logger(__name__).debug('Unpacking with format: {}'.format(unpack_fmt))
        return struct.unpack(unpack_fmt, rx)

    @classmethod
    def _rx_ext_packet(cls, msg: Message, command: int, rx_length: int, check_ack: bool = True,
                       check_length: bool = True) -> Message:
        """
        Parse a received packet
        :param msg: data to parse
        :param command: The extended command sent
        :param rx_length: Expected length of the received data
        :param check_ack: If true, checks the first byte as an AK byte
        :param tx_payload: what was sent, used if an exception needs to be thrown
        :return: The payload of the extended message
        """
        assert (msg['command'] == 0x56)
        if not cls.VEX_CRC16.compute(msg.rx) == 0:
            raise VEXCommError("CRC of message didn't match 0: {}".format(cls.VEX_CRC16.compute(msg.rx)), msg)
        assert (msg['payload'][0] == command)
        msg = msg['payload'][1:-2]
        if check_ack:
            nacks = {
                0xFF: "General NACK",
                0xCE: "CRC error on recv'd packet",
                0xD0: "Payload too small",
                0xD1: "Request transfer size too large",
                0xD2: "Program CRC error",
                0xD3: "Program file error",
                0xD4: "Attempted to download/upload uninitialized",
                0xD5: "Initialization invalid for this function",
                0xD6: "Data not a multiple of 4 bytes",
                0xD7: "Packet address does not match expected",
                0xD8: "Data downloaded does not match initial length",
                0xD9: "Directory entry does not exist",
                0xDA: "Max user files, no more room for another user program",
                0xDB: "User file exists"
            }
            if msg[0] in nacks.keys():
                raise VEXCommError("Device NACK'd with reason: {}".format(nacks[msg[0]]), msg)
            elif msg[0] != cls.ACK_BYTE:
                raise VEXCommError("Device didn't ACK", msg)
            msg = msg[1:]
        if len(msg) > 0:
            logger(cls).debug('Set msg window to {}'.format(bytes_to_str(msg)))
        if len(msg) != rx_length and check_length:
            raise VEXCommError("Received length doesn't match {} (got {})".format(rx_length, len(msg)), msg)
        return msg

    def _txrx_ext_packet(self, command: int, tx_data: Union[Iterable, bytes, bytearray],
                         rx_length: int, check_length: bool = True,
                         check_ack: bool = True, timeout: float = 0.1) -> Message:
        """
        Transmits and receives an extended command to the V5.
        :param command: Extended command code
        :param tx_data: Tranmission payload
        :param rx_length: Expected length of the received extended payload
        :param rx_wait: Amount of time to wait after transmitting the packet before reading the response
        :param check_ack: If true, then checks the first byte of the extended payload as an AK byte
        :return: A bytearray of the extended payload
        """
        tx_payload = self._form_extended_payload(command, tx_data)
        rx = self._txrx_packet(0x56, tx_data=tx_payload, timeout=timeout)

        return self._rx_ext_packet(rx, command, rx_length, check_ack=check_ack, check_length=check_length)

    @classmethod
    def _form_extended_payload(cls, msg: int, payload: Union[Iterable, bytes, bytearray]) -> bytearray:
        if payload is None:
            payload = bytearray()
        payload_length = len(payload)
        assert payload_length <= 0x7f_ff
        if payload_length >= 0x80:
            payload_length = [(payload_length >> 8) | 0x80, payload_length & 0xff]
        else:
            payload_length = [payload_length]
        packet = bytearray([msg, *payload_length, *payload])
        crc = cls.VEX_CRC16.compute(bytes([*cls._form_simple_packet(0x56), *packet]))
        packet = bytearray([*packet, crc >> 8, crc & 0xff])
        assert (cls.VEX_CRC16.compute(bytes([*cls._form_simple_packet(0x56), *packet])) == 0)
        return packet
