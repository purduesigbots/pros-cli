import click
import serial
import prosflasher.upload
import time
from proscli.utils import debug
from prosflasher import adr_to_str, bytes_to_str

ACK = 0x79
MAX_WRITE_SIZE = 256


def debug_response(command, response, fmt='STM BL RESPONSE TO 0x{}: {}'):
    if not isinstance(command, str):
        command = bytes_to_str(command)
    if not isinstance(response, str):
        response = bytes_to_str(response)
    debug(fmt.format(command, response))


def send_bootloader_command(port, command, response_size=1):
    port.write([command, 0xff - command])
    port.flush()
    response = port.read(response_size)
    debug_response(command, response)
    return response


def compute_address_commandable(address):
    """
    Creates a commandable address, with the checksum appended
    :param address: A list of bytes corresponding to the address or the actual address in question
    :return: A list of bytes corresponding to the address with the checksum appended
    """
    if not isinstance(address, bytearray):
        if isinstance(address, bytes) or isinstance(address, list):
            address = bytearray(address)
        else:
            address = [(address >> 24) & 0xff, (address >> 16) & 0xff, (address >> 8) & 0xff, address & 0xff]
    checksum = 0x00
    for x in address:
        checksum ^= x
    address.append(checksum)
    return address


def prepare_bootloader(port):
    click.echo('Preparing bootloader...', nl=False)
    prosflasher.upload.configure_port(port, serial.PARITY_EVEN)
    port.write([0x7f])
    port.flush()
    response = port.read(1)
    debug_response(0x07f, response)
    if response is None or len(response) != 1 or response[0] != ACK:
        click.echo('failed')
        return False
    click.echo('complete')
    if click.get_current_context().obj.verbosity > 1:
        click.echo('Extra commands:')
        send_bootloader_command(port, 0x00, 15)
        send_bootloader_command(port, 0x01, 5)
        send_bootloader_command(port, 0x02, 5)
    return True


def read_memory(port, start_address, size=0x100):
    size -= 1
    start_address = compute_address_commandable(start_address)
    click.echo('Reading {} bytes from 0x{}...'.format(size, ''.join('{:02X}'.format(x) for x in start_address[:-1])))
    response = send_bootloader_command(port, 0x11)
    if response is None or response[0] != 0x79:
        click.echo('failed (could not begin read)')
        return False
    port.write(start_address)
    port.flush()
    response = port.read(1)
    debug_response('address', response)
    if response is None or response[0] != 0x79:
        click.echo('failed (address not accepted)')
        return False
    click.echo(''.join('0x{:02X} '.format(x) for x in [size, 0xff - size]))
    port.write([size, 0xff - size])
    port.flush()
    response = port.read(1)
    debug_response('size', response)
    if response is None or response[0] != 0x79:
        click.echo('failed (size not accepted)')
        return False
    data = port.read(size + 1)
    if data is not None:
        click.echo('DATA: ' + ''.join('0x{:02X} '.format(x) for x in data))
    data = port.read_all()
    if data is not None:
        click.echo('EXTRA DATA: ' + ''.join('0x{:02X} '.format(x) for x in data))
    return True


def erase_flash(port):
    click.echo('Erasing user flash...', nl=False)
    prosflasher.upload.configure_port(port, serial.PARITY_EVEN)
    response = send_bootloader_command(port, 0x43, 1)
    if response is None or response[0] != 0x79:
        click.echo('failed')
        return False
    response = send_bootloader_command(port, 0xff, 1)
    if response is None or response[0] != 0x79:
        click.echo('failed')
        return False
    click.echo('complete')
    return True


def write_flash(port, start_address, data):
    data = bytearray(data)
    if len(data) > 256:
        click.echo('Tried writing too much data at once! ({} bytes)'.format(len(data)))
        return False
    port.read_all()
    start_address = compute_address_commandable(start_address)
    debug('Writing {} bytes to {}'.format(len(data), adr_to_str(start_address)))
    response = send_bootloader_command(port, 0x31)
    if response is None or response[0] != ACK:
        click.echo('failed (write command not accepted)')
        return False
    port.write(start_address)
    port.flush()
    response = port.read(1)
    debug_response(adr_to_str(start_address), response)
    if response is None or response[0] != ACK:
        click.echo('failed (address not accepted)')
        return False
    checksum = len(data) - 1
    for x in data:
        checksum ^= x
    data.insert(0, len(data) - 1)
    data.append(checksum)
    port.write(data)
    time.sleep(0.005)
    response = port.read(1)
    if response is None or response[0] != ACK:
        port.write(data)
        time.sleep(20)
        response = port.read(1)
        if response is None or response[0] != ACK:
            click.echo('failed (could not complete upload)')
            return False
    port.flush()
    port.reset_input_buffer()
    return True


def upload_binary(port, file):
    address = 0x08000000
    with open(file, 'rb') as f:
        data = bytes(f.read())
        data_segments = [data[x:x+MAX_WRITE_SIZE] for x in range(0, len(data), MAX_WRITE_SIZE)]
        with click.progressbar(data_segments, label='Uploading binary to Cortex...') as segments:
            for segment in segments:
                if not write_flash(port, address, segment):
                    return False
                address += 0x100
    return True


def send_go_command(port, address):
    click.echo('Executing binary...', nl=False)
    address = compute_address_commandable(address)
    debug('Executing binary at {}'.format(adr_to_str(address)))

    response = send_bootloader_command(port, 0x21, 1)
    if response is None or response[0] != ACK:
        click.echo('failed (execute command not accepted)')
        return False
    port.write(address)
    port.flush()
    click.echo('complete')
    return True


