import gzip
import io
import re
import struct
import time
import typing
from collections import defaultdict
from configparser import ConfigParser
from datetime import datetime, timedelta
from enum import IntEnum, IntFlag
from io import BytesIO, StringIO
from pathlib import Path
from typing import *
from typing import BinaryIO

from semantic_version import Spec

from pros.common import ui
from pros.common import *
from pros.conductor import Project
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
    joystick_ports = [p for p in ports if filter_v5_ports(p, ['1'], ['Controller'])]

    # Testing this code path is hard!
    if len(user_ports) != len(system_ports):
        if len(user_ports) > len(system_ports):
            user_ports = [p for p in user_ports if p not in system_ports]
        else:
            system_ports = [p for p in system_ports if p not in user_ports]

    if len(user_ports) == len(system_ports) and len(user_ports) > 0:
        if p_type.lower() == 'user':
            return user_ports
        elif p_type.lower() == 'system':
            return system_ports + joystick_ports
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
            return [ports[0], *joystick_ports]
        else:
            raise ValueError(f'Invalid port type specified: {p_type}')
    # these can now also be used as user ports
    if len(joystick_ports) > 0:  # and p_type.lower() == 'system':
        return joystick_ports
    return []


def with_download_channel(f):
    """
    Function decorator for use inside V5Device class. Needs to be outside the class because @staticmethod prevents
    us from making a function decorator
    """

    def wrapped(device, *args, **kwargs):
        with V5Device.DownloadChannel(device):
            return f(device, *args, **kwargs)

    return wrapped


def compress_file(file: BinaryIO, file_len: int, label='Compressing binary') -> Tuple[BinaryIO, int]:
    buf = io.BytesIO()
    with ui.progressbar(length=file_len, label=label) as progress:
        with gzip.GzipFile(fileobj=buf, mode='wb', mtime=0) as f:
            while True:
                data = file.read(16 * 1024)
                if not data:
                    break
                f.write(data)
                progress.update(len(data))
    # recompute file length
    file_len = buf.seek(0, 2)
    buf.seek(0, 0)
    return buf, file_len


class V5Device(VEXDevice, SystemDevice):
    vid_map = {'user': 1, 'system': 15, 'rms': 16, 'pros': 24, 'mw': 32}  # type: Dict[str, int]
    channel_map = {'pit': 0, 'download': 1}  # type: Dict[str, int]

    class FTCompleteOptions(IntEnum):
        DONT_RUN = 0
        RUN_IMMEDIATELY = 0b01
        RUN_SCREEN = 0b11

    VEX_CRC16 = CRC(16, 0x1021)  # CRC-16-CCIT
    VEX_CRC32 = CRC(32, 0x04C11DB7)  # CRC-32 (the one used everywhere but has no name)

    class SystemVersion(object):
        class Product(IntEnum):
            CONTROLLER = 0x11
            BRAIN = 0x10

        class BrainFlags(IntFlag):
            pass

        class ControllerFlags(IntFlag):
            CONNECTED = 0x02

        flag_map = {Product.BRAIN: BrainFlags, Product.CONTROLLER: ControllerFlags}

        def __init__(self, data: tuple):
            from semantic_version import Version
            self.system_version = Version('{}.{}.{}-{}.{}'.format(*data[0:5]))
            self.product = V5Device.SystemVersion.Product(data[5])
            self.product_flags = self.flag_map[self.product](data[6])

        def __str__(self):
            return f'System Version: {self.system_version}\n' \
                f'       Product: {self.product.name}\n' \
                f' Product Flags: {self.product_flags.value:x}'

    class SystemStatus(object):
        def __init__(self, data: tuple):
            from semantic_version import Version
            self.system_version = Version('{}.{}.{}-{}'.format(*data[0:4]))
            self.cpu0_version = Version('{}.{}.{}-{}'.format(*data[4:8]))
            self.cpu1_version = Version('{}.{}.{}-{}'.format(*data[8:12]))
            self.touch_version = data[12]
            self.system_id = data[13]

        def __getitem__(self, item):
            return self.__dict__[item]

    def __init__(self, port: BasePort):
        self._status = None
        self._serial_cache = b''
        super().__init__(port)

    class DownloadChannel(object):
        def __init__(self, device: 'V5Device', timeout: float = 5.):
            self.device = device
            self.timeout = timeout
            self.did_switch = False

        def __enter__(self):
            version = self.device.query_system_version()
            if version.product == V5Device.SystemVersion.Product.CONTROLLER:
                self.device.default_timeout = 2.
                if V5Device.SystemVersion.ControllerFlags.CONNECTED not in version.product_flags:
                    raise VEXCommError('V5 Controller doesn\'t appear to be connected to a V5 Brain', version)
                ui.echo('Transferring V5 to download channel')
                self.device.ft_transfer_channel('download')
                self.did_switch = True
                logger(__name__).debug('Sleeping for a while to let V5 start channel transfer')
                time.sleep(.25)  # wait at least 250ms before starting to poll controller if it's connected yet
                version = self.device.query_system_version()
                start_time = time.time()
                # ask controller every 25 ms if it's connected until it is
                while V5Device.SystemVersion.ControllerFlags.CONNECTED not in version.product_flags and \
                        time.time() - start_time < self.timeout:
                    version = self.device.query_system_version()
                    time.sleep(0.25)
                if V5Device.SystemVersion.ControllerFlags.CONNECTED not in version.product_flags:
                    raise VEXCommError('Could not transfer V5 Controller to download channel', version)
                logger(__name__).info('V5 should been transferred to higher bandwidth download channel')
                return self
            else:
                return self

        def __exit__(self, *exc):
            if self.did_switch:
                self.device.ft_transfer_channel('pit')
                ui.echo('V5 has been transferred back to pit channel')

    @property
    def status(self):
        if not self._status:
            self._status = self.get_system_status()
        return self._status

    @property
    def can_compress(self):
        return self.status['system_version'] in Spec('>=1.0.5')

    @property
    def is_wireless(self):
        version = self.query_system_version()
        return version.product == V5Device.SystemVersion.Product.CONTROLLER and \
               V5Device.SystemVersion.ControllerFlags.CONNECTED in version.product_flags

    def generate_cold_hash(self, project: Project, extra: dict):
        keys = {k: t.version for k, t in project.templates.items()}
        keys.update(extra)
        from hashlib import md5
        from base64 import b64encode
        msg = str(sorted(keys, key=lambda t: t[0])).encode('ascii')
        name = b64encode(md5(msg).digest()).rstrip(b'=').decode('ascii')
        if Spec('<=1.0.0-27').match(self.status['cpu0_version']):
            # Bug prevents linked files from being > 18 characters long.
            # 17 characters is probably good enough for hash, so no need to fail out
            name = name[:17]
        return name

    def upload_project(self, project: Project, **kwargs):
        assert project.target == 'v5'
        monolith_path = project.location.joinpath(project.output)
        if monolith_path.exists():
            logger(__name__).debug(f'Monolith exists! ({monolith_path})')
        if 'hot_output' in project.templates['kernel'].metadata and \
                'cold_output' in project.templates['kernel'].metadata:
            hot_path = project.location.joinpath(project.templates['kernel'].metadata['hot_output'])
            cold_path = project.location.joinpath(project.templates['kernel'].metadata['cold_output'])
            upload_hot_cold = False
            if hot_path.exists() and cold_path.exists():
                logger(__name__).debug(f'Hot and cold files exist! ({hot_path}; {cold_path})')
                if monolith_path.exists():
                    monolith_mtime = monolith_path.stat().st_mtime
                    hot_mtime = hot_path.stat().st_mtime
                    logger(__name__).debug(f'Monolith last modified: {monolith_mtime}')
                    logger(__name__).debug(f'Hot last modified: {hot_mtime}')
                    if hot_mtime > monolith_mtime:
                        upload_hot_cold = True
                        logger(__name__).debug('Hot file is newer than monolith!')
                else:
                    upload_hot_cold = True
            if upload_hot_cold:
                with hot_path.open(mode='rb') as hot:
                    with cold_path.open(mode='rb') as cold:
                        kwargs['linked_file'] = cold
                        kwargs['linked_remote_name'] = self.generate_cold_hash(project, {})
                        kwargs['linked_file_addr'] = int(
                            project.templates['kernel'].metadata.get('cold_addr', 0x03800000))
                        kwargs['addr'] = int(project.templates['kernel'].metadata.get('hot_addr', 0x07800000))
                        return self.write_program(hot, **kwargs)
        if not monolith_path.exists():
            raise ui.dont_send(Exception('No output files were found! Have you built your project?'))
        with monolith_path.open(mode='rb') as pf:
            return self.write_program(pf, **kwargs)

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

    @with_download_channel
    def write_program(self, file: typing.BinaryIO, remote_name: str = None, ini: ConfigParser = None, slot: int = 0,
                      file_len: int = -1, run_after: FTCompleteOptions = FTCompleteOptions.DONT_RUN,
                      target: str = 'flash', quirk: int = 0, linked_file: Optional[typing.BinaryIO] = None,
                      linked_remote_name: Optional[str] = None, linked_file_addr: Optional[int] = None,
                      compress_bin: bool = True, **kwargs):
        with ui.Notification():
            action_string = f'Uploading program "{remote_name}"'
            finish_string = f'Finished uploading "{remote_name}"'
            if hasattr(file, 'name'):
                action_string += f' ({Path(file.name).name})'
                finish_string += f' ({Path(file.name).name})'
            action_string += f' to V5 slot {slot + 1} on {self.port}'
            if compress_bin:
                action_string += ' (compressed)'
            ui.echo(action_string)

            remote_base = f'slot_{slot + 1}'
            if target == 'ddr':
                self.write_file(file, f'{remote_base}.bin', file_len=file_len, type='bin',
                                target='ddr', run_after=run_after, linked_filename=linked_remote_name, **kwargs)
                return
            if not isinstance(ini, ConfigParser):
                ini = ConfigParser()
            if not remote_name:
                remote_name = file.name
            if len(remote_name) > 23:
                logger(__name__).info('Truncating remote name to {} for length.'.format(remote_name[:20]))
                remote_name = remote_name[:23]

            ini_file = self.generate_ini_file(remote_name=remote_name, slot=slot, ini=ini, **kwargs)
            logger(__name__).info(f'Created ini: {ini_file}')

            if linked_file is not None:
                self.upload_library(linked_file, remote_name=linked_remote_name, addr=linked_file_addr,
                                    compress=compress_bin, force_upload=kwargs.pop('force_upload_linked', False))
            bin_kwargs = {k: v for k, v in kwargs.items() if v in ['addr']}
            if (quirk & 0xff) == 1:
                # WRITE BIN FILE
                self.write_file(file, f'{remote_base}.bin', file_len=file_len, type='bin', run_after=run_after,
                                linked_filename=linked_remote_name, compress=compress_bin, **bin_kwargs, **kwargs)
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
                                linked_filename=linked_remote_name, compress=compress_bin, **bin_kwargs, **kwargs)
            else:
                raise ValueError(f'Unknown quirk option: {quirk}')
            ui.finalize('upload', f'{finish_string} to V5')

    def ensure_library_space(self, name: Optional[str] = None, vid: int_str = None,
                             target_name: Optional[str] = None):
        """
        Uses algorithms, for loops, and if statements to determine what files should be removed

        This method searches for any orphaned files:
            - libraries without any user files linking to it
            - user files whose link does not exist
        and removes them without prompt

        It will also ensure that only 3 libraries are being used on the V5.
        If there are more than 3 libraries, then the oldest libraries are elected for eviction after a prompt.
        "oldest" is determined by the most recently uploaded library or program linking to that library
        """
        assert not (vid is None and name is not None)
        used_libraries = []
        if vid is not None:
            if isinstance(vid, str):
                vid = self.vid_map[vid.lower()]
            # assume all libraries
            unused_libraries = [
                (vid, l['filename'])
                for l
                in [self.get_file_metadata_by_idx(i)
                    for i in range(0, self.get_dir_count(vid=vid))
                    ]
            ]
            if name is not None:
                if (vid, name) in unused_libraries:
                    # we'll be overwriting the library anyway, so remove it as a candidate for removal
                    unused_libraries.remove((vid, name))
                used_libraries.append((vid, name))
        else:
            unused_libraries = []

        programs: Dict[str, Dict] = {
            # need the linked file metadata, so we have to use the get_file_metadata_by_name command
            p['filename']: self.get_file_metadata_by_name(p['filename'], vid='user')
            for p
            in [self.get_file_metadata_by_idx(i)
                for i in range(0, self.get_dir_count(vid='user'))]
            if p['type'] == 'bin'
        }
        library_usage: Dict[Tuple[int, str], List[str]] = defaultdict(list)
        for program_name, metadata in programs.items():
            library_usage[(metadata['linked_vid'], metadata['linked_filename'])].append(program_name)

        orphaned_files: List[Union[str, Tuple[int, str]]] = []
        for link, program_names in library_usage.items():
            linked_vid, linked_name = link
            if name is not None and linked_vid == vid and linked_name == name:
                logger(__name__).debug(f'{program_names} will be removed because the library will be replaced')
                orphaned_files.extend(program_names)
            elif linked_vid != 0:  # linked_vid == 0 means there's no link. Can't be orphaned if there's no link
                if link in unused_libraries:
                    # the library is being used
                    logger(__name__).debug(f'{link} is being used')
                    unused_libraries.remove(link)
                    used_libraries.append(link)
                else:
                    try:
                        self.get_file_metadata_by_name(linked_name, vid=linked_vid)
                        logger(__name__).debug(f'{link} exists')
                        used_libraries.extend(link)
                    except VEXCommError as e:
                        logger(__name__).debug(dont_send(e))
                        logger(__name__).debug(f'{program_names} will be removed because {link} does not exist')
                        orphaned_files.extend(program_names)
        orphaned_files.extend(unused_libraries)
        if target_name is not None and target_name in orphaned_files:
            # the file will be overwritten anyway
            orphaned_files.remove(target_name)
        if len(orphaned_files) > 0:
            logger(__name__).warning(f'Removing {len(orphaned_files)} orphaned file(s) ({orphaned_files})')
            for file in orphaned_files:
                if isinstance(file, tuple):
                    self.erase_file(file_name=file[1], vid=file[0])
                else:
                    self.erase_file(file_name=file, erase_all=True, vid='user')

        if len(used_libraries) > 3:
            libraries = [
                (linked_vid, linked_name, self.get_file_metadata_by_name(linked_name, vid=linked_vid)['timestamp'])
                for linked_vid, linked_name
                in used_libraries
            ]
            library_usage_timestamps = sorted([
                (
                    linked_vid,
                    linked_name,
                    # get the most recent timestamp of the library and all files linking to it
                    max(linked_timestamp, *[programs[p]['timestamp'] for p in library_usage[(linked_vid, linked_name)]])
                )
                for linked_vid, linked_name, linked_timestamp
                in libraries
            ], key=lambda t: t[2])
            evicted_files: List[Union[str, Tuple[int, str]]] = []
            evicted_file_list = ''
            for evicted_library in library_usage_timestamps[:3]:
                evicted_files.append(evicted_library[0:2])
                evicted_files.extend(library_usage[evicted_library[0:2]])
                evicted_file_list += evicted_library[1] + ', '
                evicted_file_list += ', '.join(library_usage[evicted_file_list[0:2]])
            evicted_file_list = evicted_file_list[:2]  # remove last ", "
            assert len(evicted_files) > 0
            if confirm(f'There are too many files on the V5. PROS can remove the following suggested old files: '
                       f'{evicted_file_list}',
                       title='Confirm file eviction plan:'):
                for file in evicted_files:
                    if isinstance(file, tuple):
                        self.erase_file(file_name=file[1], vid=file[0])
                    else:
                        self.erase_file(file_name=file, erase_all=True, vid='user')

    def upload_library(self, file: typing.BinaryIO, remote_name: str = None, file_len: int = -1, vid: int_str = 'pros',
                       force_upload: bool = False, compress: bool = True, **kwargs):
        """
        Upload a file used for linking. Contains the logic to check if the file is already present in the filesystem
        and to prompt the user if we need to evict a library (and user programs).

        If force_upload is true, then skips the "is already present in the filesystem check"
        """
        if not remote_name:
            remote_name = file.name
        if len(remote_name) > 23:
            logger(__name__).info('Truncating remote name to {} for length.'.format(remote_name[:23]))
            remote_name = remote_name[:23]

        if file_len < 0:
            file_len = file.seek(0, 2)
            file.seek(0, 0)

        if compress and self.can_compress:
            file, file_len = compress_file(file, file_len, label='Compressing library')

        crc32 = self.VEX_CRC32.compute(file.read(file_len))
        file.seek(0, 0)

        if not force_upload:
            try:
                response = self.get_file_metadata_by_name(remote_name, vid)
                logger(__name__).debug(response)
                logger(__name__).debug({'file len': file_len, 'crc': crc32})
                if response['size'] == file_len and response['crc'] == crc32:
                    ui.echo('Library is already onboard V5')
                    return
                else:
                    logger(__name__).warning(f'Library onboard doesn\'t match! '
                                             f'Length was {response["size"]} but expected {file_len} '
                                             f'CRC: was {response["crc"]:x} but expected {crc32:x}')
            except VEXCommError as e:
                logger(__name__).debug(e)
        else:
            logger(__name__).info('Skipping already-uploaded checks')

        logger(__name__).debug('Going to worry about uploading the file now')
        self.ensure_library_space(remote_name, vid, )
        self.write_file(file, remote_name, file_len, vid=vid, **kwargs)

    def read_file(self, file: typing.IO[bytes], remote_file: str, vid: int_str = 'user', target: int_str = 'flash',
                  addr: Optional[int] = None, file_len: Optional[int] = None):
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        if addr is None:
            metadata = self.get_file_metadata_by_name(remote_file, vid=vid)
            addr = metadata['addr']
        wireless = self.is_wireless
        ft_meta = self.ft_initialize(remote_file, function='download', vid=vid, target=target, addr=addr)
        if file_len is None:
            file_len = ft_meta['file_size']

        if wireless and file_len > 0x25000:
            confirm(f'You\'re about to download {file_len} bytes wirelessly. This could take some time, and you should '
                    f'consider downloading directly with a wire.', abort=True, default=False)

        max_packet_size = ft_meta['max_packet_size']
        with ui.progressbar(length=file_len, label='Downloading {}'.format(remote_file)) as progress:
            for i in range(0, file_len, max_packet_size):
                packet_size = max_packet_size
                if i + max_packet_size > file_len:
                    packet_size = file_len - i
                file.write(self.ft_read(addr + i, packet_size))
                progress.update(packet_size)
                logger(__name__).debug('Completed {} of {} bytes'.format(i + packet_size, file_len))
        self.ft_complete()

    def write_file(self, file: typing.BinaryIO, remote_file: str, file_len: int = -1,
                   run_after: FTCompleteOptions = FTCompleteOptions.DONT_RUN, linked_filename: Optional[str] = None,
                   linked_vid: int_str = 'pros', compress: bool = False, **kwargs):
        if file_len < 0:
            file_len = file.seek(0, 2)
            file.seek(0, 0)
        display_name = remote_file
        if hasattr(file, 'name'):
            display_name = f'{remote_file} ({Path(file.name).name})'
        if compress and self.can_compress:
            file, file_len = compress_file(file, file_len)

        if self.is_wireless and file_len > 0x25000:
            confirm(f'You\'re about to upload {file_len} bytes wirelessly. This could take some time, and you should '
                    f'consider uploading directly with a wire.', abort=True, default=False)
        crc32 = self.VEX_CRC32.compute(file.read(file_len))
        file.seek(0, 0)
        addr = kwargs.get('addr', 0x03800000)
        logger(__name__).info('Transferring {} ({} bytes) to the V5 from {}'.format(remote_file, file_len, file))
        ft_meta = self.ft_initialize(remote_file, function='upload', length=file_len, crc=crc32, **kwargs)
        if linked_filename is not None:
            logger(__name__).debug('Setting file link')
            self.ft_set_link(linked_filename, vid=linked_vid)
        assert ft_meta['file_size'] >= file_len
        if len(remote_file) > 24:
            logger(__name__).info('Truncating {} to {} due to length'.format(remote_file, remote_file[:24]))
            remote_file = remote_file[:24]
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

    @with_download_channel
    def capture_screen(self) -> Tuple[List[List[int]], int, int]:
        self.sc_init()
        width, height = 512, 272
        file_size = width * height * 4  # ARGB

        rx_io = BytesIO()
        self.read_file(rx_io, '', vid='system', target='screen', addr=0, file_len=file_size)
        rx = rx_io.getvalue()
        rx = struct.unpack('<{}I'.format(len(rx) // 4), rx)

        data = [[] for _ in range(height)]
        for y in range(height):
            for x in range(width - 1):
                if x < 480:
                    px = rx[y * width + x]
                    data[y].append((px & 0xff0000) >> 16)
                    data[y].append((px & 0x00ff00) >> 8)
                    data[y].append(px & 0x0000ff)

        return data, 480, height

    def used_slots(self) -> Dict[int, Optional[str]]:
        with ui.Notification():
            rv = {}
            for slot in range(1, 9):
                ini = self.read_ini(f'slot_{slot}.ini')
                rv[slot] = ini['program']['name'] if ini is not None else None
            return rv

    def read_ini(self, remote_name: str) -> Optional[ConfigParser]:
        try:
            rx_io = BytesIO()
            self.read_file(rx_io, remote_name)
            config = ConfigParser()
            rx_io.seek(0, 0)
            config.read_string(rx_io.read().decode('ascii'))
            return config
        except VEXCommError as e:
            return None

    @retries
    def query_system_version(self) -> SystemVersion:
        logger(__name__).debug('Sending simple 0xA408 command')
        ret = self._txrx_simple_struct(0xA4, '>8B')
        logger(__name__).debug('Completed simple 0xA408 command')
        return V5Device.SystemVersion(ret)

    @retries
    def ft_transfer_channel(self, channel: int_str):
        logger(__name__).debug(f'Transferring to {channel} channel')
        logger(__name__).debug('Sending ext 0x10 command')
        if isinstance(channel, str):
            channel = self.channel_map[channel]
        assert isinstance(channel, int) and 0 <= channel <= 1
        self._txrx_ext_packet(0x10, struct.pack('<2B', 1, channel), rx_length=0)
        logger(__name__).debug('Completed ext 0x10 command')

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
            'type': 'bin',
            'timestamp': datetime.now(),
            'version': 0x01_00_00_00,
            'name': file_name
        }
        options.update({k: v for k, v in kwargs.items() if k in options and v is not None})

        if isinstance(options['function'], str):
            options['function'] = {'upload': 1, 'download': 2}[options['function'].lower()]
        if isinstance(options['target'], str):
            options['target'] = {'ddr': 0, 'flash': 1, 'screen': 2}[options['target'].lower()]
        if isinstance(options['vid'], str):
            options['vid'] = self.vid_map[options['vid'].lower()]
        if isinstance(options['type'], str):
            options['type'] = options['type'].encode(encoding='ascii')
        if isinstance(options['name'], str):
            options['name'] = options['name'].encode(encoding='ascii')
        options['options'] |= 1 if options['overwrite'] else 0
        options['timestamp'] = int((options['timestamp'] - datetime(2000, 1, 1)).total_seconds())

        logger(__name__).debug('Initializing file transfer w/: {}'.format(options))
        tx_payload = struct.pack("<4B3I4s2I24s", options['function'], options['target'], options['vid'],
                                 options['options'], options['length'], options['addr'], options['crc'],
                                 options['type'], options['timestamp'], options['version'], options['name'])
        rx = self._txrx_ext_struct(0x11, tx_payload, "<H2I", timeout=kwargs.get('timeout', self.default_timeout * 5))
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
        ret = self._txrx_ext_packet(0x12, tx_payload, 0, timeout=self.default_timeout * 10)
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
        actual_n_bytes = n_bytes + (0 if n_bytes % 4 == 0 else 4 - n_bytes % 4)
        ui.logger(__name__).debug(dict(actual_n_bytes=actual_n_bytes, addr=addr))
        tx_payload = struct.pack("<IH", addr, actual_n_bytes)
        rx_fmt = "<I{}s".format(actual_n_bytes)
        ret = self._txrx_ext_struct(0x14, tx_payload, rx_fmt, check_ack=False)[1][:n_bytes]
        logger(__name__).debug('Completed ext 0x14 command')
        return ret

    @retries
    def ft_set_link(self, link_name: str, vid: int_str = 'user', options: int = 0):
        logger(__name__).debug('Sending ext 0x15 command')
        if isinstance(vid, str):
            vid = self.vid_map[vid.lower()]
        if isinstance(link_name, str):
            link_name = link_name.encode(encoding='ascii')
        logger(__name__).debug(f'Linking current ft to {link_name} (vid={vid})')
        tx_payload = struct.pack("<2B24s", vid, options, link_name)
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
        rx = self._txrx_ext_struct(0x17, tx_payload, "<B3L4sLL24s")
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
        logger(__name__).debug('VID: {}\tOptions: {}\tFile name: {}\tRun: {}'.format(vid, options, file_name, run))
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
        ui.logger(__name__).debug(f'Options: {dict(vid=vid, file_name=file_name)}')
        tx_payload = struct.pack("<2B24s", vid, options, file_name.encode(encoding='ascii'))
        rx = self._txrx_ext_struct(0x19, tx_payload, "<B3L4sLL24s")
        rx = dict(zip(['linked_vid', 'size', 'addr', 'crc', 'type', 'timestamp', 'version', 'linked_filename'], rx))
        logger(__name__).debug(rx)
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
            'addr': 0xff_ff_ff_ff,
            'type': b'\xff\xff\xff\xff',
            'timestamp': 0xff_ff_ff_ff,
            'version': 0xff_ff_ff_ff
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
    def get_system_status(self) -> SystemStatus:
        logger(__name__).debug('Sending ext 0x22 command')
        rx = self._txrx_ext_struct(0x22, [], "<x12B3xBI12x")
        logger(__name__).debug('Completed ext 0x22 command')
        return V5Device.SystemStatus(rx)

    @retries
    def user_fifo_read(self) -> bytes:
        # I can't really think of a better way to only return when a full
        # COBS message was written than to just cache the data until we hit a \x00.

        # read/write are the same command, behavior dictated by specifying
        # length-to-read as 0xFF and providing additional payload bytes to write or
        # specifying a length-to-read and no additional data to read.
        logger(__name__).debug('Sending ext 0x27 command (read)')
        # specifying a length to read (0x40 bytes) with no additional payload data.
        tx_payload = struct.pack("<2B", self.channel_map['download'], 0x40)
        # RX length isn't always 0x40 (end of buffer reached), so don't check_length.
        self._serial_cache += self._txrx_ext_packet(0x27, tx_payload, 0, check_length=False)[1:]
        logger(__name__).debug('Completed ext 0x27 command (read)')
        # if _serial_cache doesn't have a \x00, pretend we didn't read anything.
        if b'\x00' not in self._serial_cache:
            return b''
        # _serial_cache has a \x00, split off the beginning part and hand it down.
        parts = self._serial_cache.split(b'\x00')
        ret = parts[0] + b'\x00'
        self._serial_cache = b'\x00'.join(parts[1:])

        return ret

    @retries
    def user_fifo_write(self, payload: Union[Iterable, bytes, bytearray, str]):
        raise NotImplementedError('Writing data over a wireless connection is not yet implemented')
        
        # pylint: disable=unreachable
        logger(__name__).debug('Sending ext 0x27 command (write)')
        max_packet_size = 224
        pl_len = len(payload)
        for i in range(0, pl_len, max_packet_size):
            packet_size = max_packet_size
            if i + max_packet_size > pl_len:
                packet_size = pl_len - i
            logger(__name__).debug(f'Writing {packet_size} bytes to user FIFO')
            self._txrx_ext_packet(0x27, b'\x01\x00' + payload[i:packet_size], 0, check_length=False)[1:]
        logger(__name__).debug('Completed ext 0x27 command (write)')

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
                         timeout: Optional[float] = None) -> Tuple:
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
                         check_ack: bool = True, timeout: Optional[float] = None) -> Message:
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
