import serial
import serial.tools.list_ports
from typing import *

CORTEX_USB_VID = [ 0x4d8, 0x67b ]


def create_serial(port_name: str) -> serial.Serial:
    port = serial.Serial(port_name, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    port.timeout = 0.5
    port.inter_byte_timeout = 0.2
    return port

