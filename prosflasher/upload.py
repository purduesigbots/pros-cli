import serial
import serial.serialutil
import time
import itertools
import click
import os.path
from enum import Enum
import prosflasher.ports
import prosflasher.bootloader
import proscli.utils
from proscli.utils import debug
from prosflasher import bytes_to_str
import sys

ACK = 0x79


class ConnectionType(Enum):
    unknown = -1
    serial_vexnet1 = 0x00
    serial_vexnet1_turbo = 0x01  # no known affecting difference between turbo and non-turbo
    serial_vexnet2 = 0x04
    serial_vexnet2_dl = 0x05
    serial_usb = 0x10
    direct_usb = 0x20


class SystemInfo:
    device = ''
    joystick_firmware = ''
    cortex_firmware = ''
    joystick_battery = 0.0
    cortex_battery = 0.0
    backup_battery = 0.0
    connection_type = ConnectionType.unknown
    previous_polls = 0
    byte_representation = [0x00]

    def __repr__(self):
        if self.connection_type == ConnectionType.serial_vexnet1:
            connection = '  Serial w/ VEXnet 1.0 Keys'
        elif self.connection_type == ConnectionType.serial_vexnet2:
            connection = '  Serial w/ VEXnet 2.0 Keys'
        elif self.connection_type == ConnectionType.serial_vexnet2_dl:
            connection = '  Serial w/ VEXnet 2.0 Keys (download mode)'
        elif self.connection_type == ConnectionType.serial_usb:
            connection = '  Serial w/ a USB cable'
        elif self.connection_type == ConnectionType.direct_usb:
            connection = 'Directly w/ a USB cable'
        else:
            connection = 'Unknown tether connection ({})'.format(self.connection_type)

        return \
            '''Cortex Microcontroller connected on {}
  Tether: {}
Joystick: F/W {} w/ {:1.2f}V
  Cortex: F/W {} w/ {:1.2f}V (Backup: {:1.2f}V)''' \
                .format(self.device,
                        connection,
                        self.joystick_firmware, self.joystick_battery,
                        self.cortex_firmware, self.cortex_battery, self.backup_battery)


# THIS MANAGES THE UPLOAD PROCESS FOR A GIVEN PORT/BINARY PAIR
def upload(port, binary, no_poll=False, ctx=proscli.utils.State()):
    if not os.path.isfile(binary):
        click.echo('Failed to download... file does not exist')
        return False
    port = prosflasher.ports.create_serial(port)
    if not port:
        click.echo('Failed to download: port not found')
        return
    try:
        stop_user_code(port, ctx)
        if not no_poll:
            sys_info = ask_sys_info(port, ctx)
            if sys_info is None:
                time.sleep(1.5)
                sys_info = ask_sys_info(port)
                if sys_info is None:
                    click.echo('Failed to get system info... Try again', err=True)
                    click.get_current_context().abort()
                    sys.exit(1)
            click.echo(repr(sys_info))
        else:
            sys_info = SystemInfo()
            sys_info.connection_type = ConnectionType.serial_usb  # assume this
        if sys_info.connection_type == ConnectionType.unknown:
            click.confirm('Unable to determine system type. It may be necessary to press the '
                          'programming button on the programming kit. Continue?', abort=True, default=True)
        if sys_info.connection_type == ConnectionType.serial_vexnet2:
            # need to send to download channel
            if not send_to_download_channel(port):
                return False
        if not expose_bootloader(port):
            return False
        if sys_info.connection_type == ConnectionType.serial_usb:
            time.sleep(0.25)
        if not prosflasher.bootloader.prepare_bootloader(port):
            return False
        if not prosflasher.bootloader.erase_flash(port):
            return False
        if not prosflasher.bootloader.upload_binary(port, binary):
            return False
        if not prosflasher.bootloader.send_go_command(port, 0x08000000):
            return False

        reset_cortex(port)

    except serial.serialutil.SerialException as e:
        click.echo('Failed to download code! ' + str(e))
    finally:
        port.close()
    click.echo("Download complete!")
    pass


def stop_user_code(port, ctx=proscli.utils.State()):
    click.echo('Stopping user code... ', nl=False)
    stopbits = [0x0f, 0x0f, 0x21, 0xde, 0x08, 0x00, 0x00, 0x00, 0x08, 0xf1, 0x04]
    debug(bytes_to_str(stopbits), ctx)
    if not port.is_open:
        port.open()
    port.flush()
    port.read(port.in_waiting)
    for stopbit in stopbits:
        port.write([stopbit])
    port.flush()
    response = port.read_all()
    debug(bytes_to_str(response), ctx)
    port.parity = serial.PARITY_NONE
    click.echo('complete')


def ask_sys_info(port, ctx=proscli.utils.State()):
    click.echo('Asking for system information... ', nl=False)
    sys_info_bits = [0xc9, 0x36, 0xb8, 0x47, 0x21]
    if not port.is_open:
        port.open()
    configure_port(port, serial.PARITY_NONE)
    debug('SYS INFO BITS: {}  PORT CFG: {}'.format(bytes_to_str(sys_info_bits), repr(port)), ctx)
    for _ in itertools.repeat(None, 10):
        port.read(port.in_waiting)
        port.write(sys_info_bits)
        port.flush()
        time.sleep(0.1)
        response = port.read_all()
        debug('SYS INFO RESPONSE: {}'.format(bytes_to_str(response)), ctx)
        if len(response) > 14:
            response = response[:14]
        if len(response) == 14 and response[0] == 0xaa and response[1] == 0x55\
                and response[2] == 0x21 and response[3] == 0xa:  # synchronization matched
            sys_info = SystemInfo()
            sys_info.device = port.name
            sys_info.joystick_firmware = '{}.{}'.format(response[4], response[5])
            sys_info.cortex_firmware = '{}.{}'.format(response[6], response[7])
            if response[8] > 5:  # anything smaller than 5 is probably garbage from ADC
                sys_info.joystick_battery = response[8] * 0.059
            if response[9] > 5:  # anything smaller than 5 is probably garbage from ADC
                sys_info.cortex_battery = response[9] * 0.059
            if response[10] > 5:  # anything smaller than 5 is probably garbage from ADC
                sys_info.backup_battery = response[10] * 0.059
            try:
                sys_info.connection_type = ConnectionType(response[11])
            except ValueError:
                sys_info.connection_type = ConnectionType.unknown
            sys_info.previous_polls = response[13]
            sys_info.byte_representation = response
            click.echo('complete')
            return sys_info
        time.sleep(0.15)
    return None


def send_to_download_channel(port, ctx=proscli.utils.State()):
    click.echo('Sending to download channel... ', nl=False)
    download_ch_bits = [0xc9, 0x36, 0xb8, 0x47, 0x35]
    configure_port(port, serial.PARITY_EVEN)
    debug('DL CH BITS: {}  PORT CFG: {}'.format(bytes_to_str(download_ch_bits), repr(port)), ctx)
    for _ in itertools.repeat(None, 5):
        port.read(port.in_waiting)
        port.write(download_ch_bits)
        port.flush()
        time.sleep(0.25)
        response = port.read_all()
        debug('DB CH RESPONSE: {}'.format(bytes_to_str(response)), ctx)
        response = response[-1:]
        if response is not None and len(response) > 0 and response[0] == ACK:
            click.echo('complete')
            return True
    click.echo('failed')
    return False


def expose_bootloader(port, ctx=proscli.utils.State()):
    click.echo('Exposing bootloader... ', nl=False)
    bootloader_bits = [0xc9, 0x36, 0xb8, 0x47, 0x25]
    configure_port(port, serial.PARITY_NONE)
    port.flush()
    debug('EXPOSE BL BITS: {}  PORT CFG: {}'.format(bytes_to_str(bootloader_bits), repr(port)), ctx)
    port.read(port.in_waiting)
    for _ in itertools.repeat(None, 5):
        port.write(bootloader_bits)
        port.flush()
    configure_port(port, serial.PARITY_NONE)
    time.sleep(0.3)  # time delay to allow shift to download mode
    click.echo('complete')
    return True


def reset_cortex(port, ctx=proscli.utils.State()):
    click.echo('Resetting cortex...', nl=False)
    configure_port(port, serial.PARITY_NONE)
    debug('RESET CORTEX. PORT CFG: {}'.format(repr(port)), ctx)
    port.flush()
    port.read(port.in_waiting)
    port.write([20])
    port.flush()
    click.echo('complete')
    time.sleep(0.01)


def configure_port(port, parity):
    port.reset_input_buffer()
    port.reset_output_buffer()
    if port.is_open:
        port.close()
    port.open()
    port.parity = parity
    port.BAUDRATES = prosflasher.ports.BAUD_RATE


def verify_file(file):
    if not os.path.isfile(file):
        return False


def dump_cortex(port, file, verbose=False):
    if not os.path.isfile(file):
        click.echo('Failed to download... file does not exist')
        return False
    port = prosflasher.ports.create_serial(port)
    if not port:
        click.echo('Failed to download: port not found')
        return
    try:
        reset_cortex(port)
        sys_info = ask_sys_info(port)
        if sys_info is None:
            click.echo('Failed to get system info... Try again', err=True)
            click.get_current_context().abort()
            sys.exit(1)
        click.echo(repr(sys_info))
        stop_user_code(port)
        if sys_info.connection_type == ConnectionType.serial_vexnet2:
            # need to send to download channel
            if not send_to_download_channel(port):
                return False
        if not expose_bootloader(port):
            return False
        if not prosflasher.bootloader.prepare_bootloader(port):
            return False
        if not prosflasher.bootloader.erase_flash(port):
            return False

        with open(file, 'wb') as f:
            address = 0x08000000
            data = prosflasher.bootloader.read_memory(port, address, 256)
            while len(data) > 0:
                f.write(data)
                address += 0x100

    except serial.serialutil.SerialException as e:
        click.echo('Failed to download code! ' + str(e))
    finally:
        port.close()
    click.echo("Download complete!")
    pass


