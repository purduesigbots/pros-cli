from .vex_device import VexDevice, decode_bytes_to_str
from .cdc_error import CDCError
import typing
from typing import *
import click
from .. import bytes_to_str
from .crc import CRC
from datetime import datetime, timedelta
import struct
from configparser import ConfigParser
from io import BytesIO, StringIO

int_str = Union[int, str]


class V5Device(VexDevice):
    vid_map = {'user': 1, 'system': 15}  # type: Dict[str, int]
    VEX_CRC16 = CRC(16, 0x1021)  # CRC-16-CCIT
    VEX_CRC32 = CRC(32, 0x04C11DB7)  # CRC-32 (the one used everywhere but has no name)

    def write_program(self, file: typing.IO[bytes], remote_base: str, ini: ConfigParser=None, slot: int=0,
                      file_len: int=-1, **kwargs):
        if not isinstance(ini, ConfigParser):
            ini = ConfigParser()
        project_ini = ConfigParser()
        project_ini['program'] = {
            'version': '0.0.0',
            'name': remote_base,
            'slot': slot,
            'icon': 'USER999x.bmp',
            'description': 'Created with PROS',
            'date': datetime.now().isoformat()
        }
        project_ini.update(ini)
        self.write_file(file, '{}.bin'.format(remote_base), file_len=file_len, **kwargs)
        with StringIO() as ini_str:
            project_ini.write(ini_str)
            with BytesIO(ini_str.getvalue().encode(encoding='ascii')) as ini_bin:
                self.write_file(ini_bin, '{}.ini'.format(remote_base), **kwargs)

    def read_file(self, file: typing.IO[bytes], remote_file: str, vid: int_str='user', target: int_str='flash'):
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        metadata = self.get_file_metadata_by_name(remote_file, vid=vid)
        ft_meta = self.ft_initialize(remote_file, function='download', vid=vid, target=target)
        for i in range(0, ft_meta['file_size'], ft_meta['max_packet_size']):
            packet_size = ft_meta['max_packet_size']
            if i + ft_meta['max_packet_size'] > ft_meta['file_size']:
                packet_size = ft_meta['file_size'] - i
            file.write(self.ft_read(metadata['addr'] + i, packet_size))
        self.ft_complete()

    def write_file(self, file: typing.IO[bytes], remote_file: str, file_len: int=-1, **kwargs):
        if file_len < 0:
            file_len = file.seek(0, 2)
            file.seek(0, 0)
        crc32 = self.VEX_CRC32.compute(file.read(file_len))
        file.seek(-file_len, 2)
        addr = kwargs.get('addr', 0x03800000)
        ft_meta = self.ft_initialize(remote_file, function='upload', length=file_len, crc=crc32, **kwargs)
        transfer_size = min(ft_meta['file_size'], file_len)
        with click.progressbar(length=transfer_size, label='Uploading {}'.format(remote_file)) as progress:
            for i in range(0, transfer_size, ft_meta['max_packet_size']):
                packet_size = ft_meta['max_packet_size']
                if i + ft_meta['max_packet_size'] > transfer_size:
                    packet_size = transfer_size - i
                self.ft_write(addr + i, file.read(packet_size))
                progress.update(packet_size)
                print('{} of {}'.format(i + packet_size, transfer_size))
        print('finalizing')
        self.ft_complete()

    def query_system_version(self, retries: int=3) -> bytearray:
        return self._txrx_simple_packet(0xA4, 0x08, retries=retries)

    def ft_initialize(self, file_name: str, retries: int=3, **kwargs) -> Dict[str, Any]:
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
        options.update(**kwargs)

        if isinstance(options['function'], str):
            options['function'] = {'upload': 1, 'download': 2}[options['function'].lower()]
        if isinstance(options['target'], str):
            options['target'] = {'ddr': 0, 'flash': 1}[options['target'].lower()]
        if isinstance(options['vid'], str):
            options['vid'] = self.vid_map[options['vid'].lower()]
        if isinstance(options['type'], str):
            options['type'] = options['type'].encode(encoding='ascii')
        options['options'] |= 1 if options['overwrite'] else 0
        options['timestamp'] = int((options['timestamp'] - datetime(2000, 1, 1)).total_seconds())

        tx_payload = struct.pack("<4B3I4s2I24s", options['function'], options['target'], options['vid'],
                                 options['options'], options['length'], options['addr'], options['crc'],
                                 options['type'], options['timestamp'], options['version'],
                                 options['name'].encode(encoding='ascii'))
        rx = self._txrx_ext_struct(0x11, tx_payload, "<H2I", retries=retries)
        rx = dict(zip(['max_packet_size', 'file_size', 'crc'], rx))
        return rx

    def ft_complete(self, run_program: bool=False, retries: int=3):
        options = 0
        options |= (1 if run_program else 0)
        tx_payload = struct.pack("<B", options)
        return self._txrx_ext_packet(0x12, tx_payload, 0, retries=retries)

    def ft_write(self, addr: int, payload: Union[Iterable, bytes, bytearray, str], retries: int=3):
        if isinstance(payload, str):
            payload = payload.encode(encoding='ascii')
        padded_payload = bytes([*payload, *([0] * (len(payload) % 4))])
        tx_fmt = "<I{}s".format(len(padded_payload))
        tx_payload = struct.pack(tx_fmt, addr, padded_payload)
        return self._txrx_ext_packet(0x13, tx_payload, 0, retries=retries)

    def ft_read(self, addr: int, n_bytes: int, retries: int=3) -> bytearray:
        req_n_bytes = n_bytes + (n_bytes % 4)
        tx_payload = struct.pack("<IH", addr, req_n_bytes)
        rx_fmt = "<I{}s{}s".format(n_bytes, n_bytes % 4)
        return self._txrx_ext_struct(0x14, tx_payload, rx_fmt, check_ack=False,
                                     check_length=False, retries=retries)[1]

    def ft_set_link(self, link_name: str, vid: int_str='user', options: int=0, retries: int=3):
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]

        tx_payload = struct.pack("<2I24s", vid, options, link_name)
        return self._txrx_ext_packet(0x15, tx_payload, 0, retries=retries)

    def get_dir_count(self, vid: int_str=1, options: int=0, retries: int=3) \
            -> int:
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        tx_payload = struct.pack("<2B", vid, options)
        return self._txrx_ext_struct(0x16, tx_payload, "<h", retries=retries)[0]

    def get_file_metadata_by_idx(self, file_idx: int, options: int=0, retries: int=3) \
            -> Dict[str, Any]:
        tx_payload = struct.pack("<2B", file_idx, options)
        rx = self._txrx_ext_struct(0x17, tx_payload, "<B3l4sll24s", retries=retries)
        rx = dict(zip(['idx', 'size', 'addr', 'crc', 'type', 'timestamp', 'version', 'filename'], rx))
        rx['type'] = decode_bytes_to_str(rx['type'])
        rx['timestamp'] = datetime(2000, 1, 1) + timedelta(seconds=rx['timestamp'])
        rx['filename'] = decode_bytes_to_str(rx['filename'])
        return rx

    def execute_program_file(self, file_name: str, vid: int_str='user', run: bool=True, retries: int=3):
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        options = 0
        options |= (0 if run else 0x80)
        tx_payload = struct.pack("<2I", vid, options, file_name.encode(encoding='ascii'))
        return self._txrx_ext_packet(0x18, tx_payload, 0, retries=retries)

    def get_file_metadata_by_name(self, file_name: str, vid: int_str=1, options: int=0, retries: int=3) \
            -> Dict[str, Any]:
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        tx_payload = struct.pack("<2B24s", vid, options, file_name.encode(encoding='ascii'))
        rx = self._txrx_ext_struct(0x19, tx_payload, "<x3l4sll24s", retries=retries)
        rx = dict(zip(['size', 'addr', 'crc', 'type', 'timestamp', 'version', 'linked_filename'], rx))
        rx['type'] = decode_bytes_to_str(rx['type'])
        rx['timestamp'] = datetime(2000, 1, 1) + timedelta(seconds=rx['timestamp'])
        rx['linked_filename'] = decode_bytes_to_str(rx['linked_filename'])
        return rx

    def set_program_file_metadata(self, file_name: str, retries: int=3, **kwargs):
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
            assert(isinstance(options['timestamp'], datetime))
            options['timestamp'] = (options['timestamp'] - datetime(2000, 1, 1)).get_seconds()
        if isinstance(options['type'], str):
            options['type'] = options['type'].encode(encoding='ascii')
        tx_payload = struct.pack("<2BI4s2I24s", options['vid'], options['options'],
                                 options['addr'], options['type'], options['timestamp'],
                                 options['version'], file_name.encode(encoding='ascii'))
        return self._txrx_ext_packet(0x1A, tx_payload, 0, retries=retries)

    def erase_program_file(self, file_name: str, erase_all: bool=False, vid: int_str='user', retries: int=3):
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        options = 0
        options |= (0x80 if erase_all else 0)
        tx_payload = struct.pack('<2B24s', vid, options, file_name.encode(encoding='ascii'))
        return self._txrx_ext_packet(0x1B, tx_payload, 0, retries=retries)

    def get_program_file_slot(self, file_name: str, vid: int=1, options: int=0, retries: int=3) \
            -> Dict[str, Any]:
        tx_payload = struct.pack("<2B24s", vid, options, file_name.encode(encoding='ascii'))
        return self._txrx_ext_struct(0x1C, tx_payload, "<B", retries=retries)[0]

    def get_device_status(self):
        raise NotImplementedError()

    def get_system_status(self, retries: int=3) -> Dict[str, Any]:
        rx = self._txrx_ext_struct(0x22, [], "<x12B3xBI12x", retries=retries)
        return {
            'system_version': rx[0:4],
            'cpu0_version': rx[4:8],
            'cpu1_version': rx[8:12],
            'touch_version': rx[12],
            'system_id': rx[13]
        }

    def _txrx_ext_struct(self, command: int, tx_data: Union[Iterable, bytes, bytearray],
                         unpack_fmt: str, retries: int=3, check_length: bool=True, check_ack: bool=True) -> Tuple:
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
        rx = self._txrx_ext_packet(command, tx_data, struct.calcsize(unpack_fmt), retries=retries,
                                   check_length=check_length, check_ack=check_ack)
        return struct.unpack(unpack_fmt, rx)

    @classmethod
    def _rx_ext_packet(cls, rx: Dict[str, Any], command: int, rx_length: int, check_ack: bool=True,
                       check_length: bool=True, tx_payload: Union[Iterable, bytes, bytearray]=None) \
            -> bytearray:
        """
        Parse a received packet
        :param rx: data to parse
        :param command: The extended command sent
        :param rx_length: Expected length of the received data
        :param check_ack: If true, checks the first byte as an AK byte
        :param tx_payload: what was sent, used if an exception needs to be thrown
        :return: The payload of the extended message
        """
        if tx_payload is None:
            tx_payload = []  # handling default case
        assert (rx['command'] == 0x56)
        if not cls.VEX_CRC16.compute(rx['raw']) == 0:
            raise CDCError(
                "CRC of {} didn't match {}".format(bytes_to_str(rx['raw']), cls.VEX_CRC16.compute(rx['raw'])),
                bytes([*cls._form_simple_packet(0x56), *tx_payload]),
                rx['raw'])
        assert (rx['payload'][0] == command)
        rx = rx['payload'][1:-2]
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
            if rx[0] in nacks.keys():
                raise CDCError("Device NACK'd with reason: {}".format(nacks[rx[0]]),
                               bytes([*cls._form_simple_packet(0x56), *tx_payload]),
                               rx)
            elif rx[0] != cls.ACK_BYTE:
                raise CDCError("Device didn't ACK",
                               bytes([*cls._form_simple_packet(0x56), *tx_payload]),
                               rx)
            rx = rx[1:]
        if len(rx) != rx_length and check_length:
            raise CDCError("Received length doesn't match {} (got {})".format(rx_length, len(rx)),
                           bytes([*cls._form_simple_packet(0x56), *tx_payload]),
                           rx)
        return rx

    def _txrx_ext_packet(self, command: int, tx_data: Union[Iterable, bytes, bytearray],
                         rx_length: int, retries: int=3, check_length: bool=True, check_ack: bool=True) -> bytearray:
        """
        Transmits and receives an extended command to the V5.
        :param command: Extended command code
        :param tx_data: Tranmission payload
        :param rx_length: Expected length of the received extended payload
        :param retries: Number of retries to attempt to parse the output before giving up
        :param rx_wait: Amount of time to wait after transmitting the packet before reading the response
        :param check_ack: If true, then checks the first byte of the extended payload as an AK byte
        :return: A bytearray of the extended payload
        """
        try:
            tx_payload = self._form_extended_payload(command, tx_data)
            rx, retries = self._txrx_packet(0x56, tx_data=tx_payload, retries=retries)

            return self._rx_ext_packet(rx, command, rx_length, check_ack=check_ack, tx_payload=tx_payload,
                                       check_length=check_length)
        except Exception as e:
            if retries > 0:
                return self._txrx_ext_packet(command, tx_data, rx_length, retries=retries-1,
                                             check_ack=check_ack, check_length=check_length)
            else:
                raise e

    @classmethod
    def _form_extended_payload(cls, msg: int, payload: Union[Iterable, bytes, bytearray]) -> bytearray:
        if payload is None:
            payload = bytearray()
        payload_length = len(payload)
        if payload_length > 0x80:
            payload_length = [(payload_length >> 8) | 0x80, payload_length & 0x7f]
        else:
            payload_length = [payload_length]
        packet = bytearray([msg, *payload_length, *payload])
        crc = cls.VEX_CRC16.compute(bytes([*cls._form_simple_packet(0x56), *packet]))
        packet = bytearray([*packet, crc >> 8, crc & 0xff])
        assert(cls.VEX_CRC16.compute(bytes([*cls._form_simple_packet(0x56), *packet])) == 0)
        return packet
