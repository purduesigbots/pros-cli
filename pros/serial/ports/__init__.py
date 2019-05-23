from functools import lru_cache

from pros.common import logger
from serial.tools import list_ports as list_ports

from .base_port import BasePort, PortConnectionException, PortException
from .direct_port import DirectPort
# from .v5_wireless_port import V5WirelessPort


@lru_cache()
def list_all_comports():
    ports = list_ports.comports()
    logger(__name__).debug('Connected: {}'.format(';'.join([str(p.__dict__) for p in ports])))
    return ports
