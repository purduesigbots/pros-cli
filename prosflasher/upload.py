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
def upload(port, y, binary, no_poll=False, ctx=proscli.utils.State()):
    if not os.path.isfile(binary):
        click.echo('Failed to download... file does not exist')
        return False
    port = prosflasher.ports.create_serial(port, serial.PARITY_EVEN)
    if not port:
        click.echo('Failed to download: port not found')
        return
    try:
        # reset_cortex(port, ctx)
        stop_user_code(port, ctx)
        if not no_poll:
            sys_info = ask_sys_info(port, ctx)
            if sys_info is None:
                time.sleep(1.5)
                sys_info = ask_sys_info(port)
                if sys_info is None:
                    click.echo('Failed to get system info... Try again', err=True)
                    return False
            click.echo(repr(sys_info))
        else:
            sys_info = SystemInfo()
            sys_info.connection_type = ConnectionType.serial_usb  # assume this
        if sys_info.connection_type == ConnectionType.unknown and not y:
            click.confirm('Unable to determine system type. It may be necessary to press the '
                          'programming button on the programming kit. Continue?', abort=True, default=True)
        if sys_info.connection_type == ConnectionType.serial_vexnet2:
            # need to send to download channel
            if not send_to_download_channel(port):
                return False
        if not expose_bootloader(port):
            return False
        port.read_all()
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
        click.echo("Download complete!")
        return True
    except serial.serialutil.SerialException as e:
        click.echo('Failed to download code! ' + str(e))
        click.echo('Try unplugging and plugging the USB cable back in,'
                   ' as well as power-cycling the microcontroller.')
        return -1000  # stop retries in this case, because there's a problem with the port
    finally:
        port.close()


def stop_user_code(port, ctx=proscli.utils.State()):
    click.echo('Stopping user code... ', nl=False)
    stopbits = [0x0f, 0x0f, 0x21, 0xde, 0x08, 0x00, 0x00, 0x00, 0x08, 0xf1, 0x04]
    debug(bytes_to_str(stopbits), ctx)
    if not port.is_open:
        port.open()
    port.flush()
    port.read_all()
    time.sleep(0.1)
    for stopbit in stopbits:
        port.write([stopbit])
    port.flush()
    response = port.read_all()
    debug(bytes_to_str(response), ctx)
    click.echo('complete')


def ask_sys_info(port, ctx=proscli.utils.State(), silent=False):
    if not silent:
        click.echo('Asking for system information... ', nl=False)
    sys_info_bits = [0xc9, 0x36, 0xb8, 0x47, 0x21]
    if not port.is_open:
        port.open()
    debug('SYS INFO BITS: {}  PORT CFG: {}'.format(bytes_to_str(sys_info_bits), repr(port)), ctx)
    for _ in itertools.repeat(None, 10):
        port.read_all()
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
                # Mask FCS bits out of response[11]
                sys_info.connection_type = ConnectionType(response[11] & 0b00110111)
            except ValueError:
                sys_info.connection_type = ConnectionType.unknown
            sys_info.previous_polls = response[13]
            sys_info.byte_representation = response
            if not silent:
                click.echo('complete')
            return sys_info
        time.sleep(0.15)
    return None


def send_to_download_channel(port, ctx=proscli.utils.State()):
    click.echo('Sending to download channel (this may take a while)... ', nl=False)
    download_ch_bits = [0xc9, 0x36, 0xb8, 0x47, 0x35]
    debug('DL CH BITS: {}  PORT CFG: {}'.format(bytes_to_str(download_ch_bits), repr(port)), ctx)
    for _ in itertools.repeat(None, 5):
        port.read_all()
        time.sleep(0.1)
        port.write(download_ch_bits)
        port.flush()
        time.sleep(3)
        response = port.read_all()
        debug('DB CH RESPONSE: {}'.format(bytes_to_str(response)), ctx)
        response = response[-1:]
        sys_info = ask_sys_info(port, ctx, silent=True)
        if (sys_info is not None and sys_info.connection_type == ConnectionType.serial_vexnet2_dl) or (response is not None and len(response) > 0 and response[0] == ACK):
            click.echo('complete')
            return True
    click.echo('failed')
    return False


def expose_bootloader(port, ctx=proscli.utils.State()):
    click.echo('Exposing bootloader... ', nl=False)
    bootloader_bits = [0xc9, 0x36, 0xb8, 0x47, 0x25]
    port.flush()
    debug('EXPOSE BL BITS: {}  PORT CFG: {}'.format(bytes_to_str(bootloader_bits), repr(port)), ctx)
    port.read_all()
    time.sleep(0.1)
    for _ in itertools.repeat(None, 5):
        port.write(bootloader_bits)
        time.sleep(0.1)
    time.sleep(0.3)  # time delay to allow shift to download mode
    click.echo('complete')
    return True


def reset_cortex(port, ctx=proscli.utils.State()):
    click.echo('Resetting cortex... ', nl=False)
    debug('RESET CORTEX. PORT CFG: {}'.format(repr(port)), ctx)
    port.parity = serial.PARITY_NONE
    port.flush()
    port.read_all()
    time.sleep(0.1)
    port.write([0xc9, 0x36, 0xb8, 0x47, 0x20])
    port.flush()
    port.write([0x14])
    click.echo('complete')
    time.sleep(0.01)


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

