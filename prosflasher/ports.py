import click
import serial
import serial.tools.list_ports

USB_VID = [0x4d8, 0x67b]
BAUD_RATE = 115200
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS
STOP_BITS = serial.STOPBITS_ONE


def list_com_ports():
    """
    :return: Returns a list of valid serial ports that we believe are VEX Cortex Microcontrollers
    """
    return [x for x in serial.tools.list_ports.comports() if x.vid is not None and (x.vid in USB_VID or 'vex' in x.product.lower())]


def create_serial(port, parity):
    """
    Creates and/or configures a serial port to communicate with the Cortex Microcontroller
    :param port: A serial.Serial object, a device string identifier will create a corresponding serial port.
        Anything else will create a default serial port with no device assigned.
    :return: Returns a correctly configured instance of a serial.Serial object, potentially with a correctly configured
        device iff a correct port value was passed in
    """
    # port_str = ''
    if isinstance(port, str):
        try:
            # port_str = port
            port = serial.Serial(port, baudrate=BAUD_RATE, bytesize=serial.EIGHTBITS, parity=parity, stopbits=serial.STOPBITS_ONE)
        except serial.SerialException as e:
            click.echo('WARNING: {}'.format(e))
            port = serial.Serial(baudrate=BAUD_RATE, bytesize=serial.EIGHTBITS, parity=parity, stopbits=serial.STOPBITS_ONE)
    elif not isinstance(port, serial.Serial):
        click.echo('port was not string, send help')
        port = serial.Serial(baudrate=BAUD_RATE, bytesize=serial.EIGHTBITS, parity=parity, stopbits=serial.STOPBITS_ONE)

    assert isinstance(port, serial.Serial)

    # port.port = port_str if port_str != '' else None
    port.timeout = 0.5
    # port.write_timeout = 5.0
    port.inter_byte_timeout = 0.1  # todo make sure this is seconds
    return port


def create_port_list(verbose=False):
    """
    Returns a formatted string of all COM ports we believe are valid Cortex ports, delimited by \n
    :param verbose: If True, then the hwid will be added to the end of each device
    :return: A formatted string for printing describing the COM ports
    """
    out = ''
    if verbose:
        for p in list_com_ports():
            out += '{} : {} ({})\n'.format(p.device, p.description, p.hwid)
    else:
        for p in list_com_ports():
            out += '{} : {}\n'.format(p.device, p.description)
    return out
