import sys
import time
from typing import *
import os

import simplepyble

from pros.common import dont_send, logger
from pros.serial.ports.exceptions import (ConnectionRefusedException,
                                          PortNotFoundException)

from .base_port import BasePort, PortConnectionException

MAX_PACKET_SIZE = 244


class SuppressStdout:
    def __enter__(self):
        with open(os.devnull, 'w') as devnull:
            self.orig_stdout_fno = os.dup(sys.stdout.fileno())
            os.dup2(devnull.fileno(), 1)

    def __exit__(self, *args):
        os.dup2(self.orig_stdout_fno, 1)


class BluetoothPort(BasePort):

    def __init__(self, port_name: str, **kwargs):

        self.UUIDs = {
            "SERVICE": "08590f7e-db05-467e-8757-72f6faeb13d5",
            "DATA_TX": "08590f7e-db05-467e-8757-72f6faeb1306",
            "DATA_RX": "08590f7e-db05-467e-8757-72f6faeb13f5",
            "USER_TX": "08590f7e-db05-467e-8757-72f6faeb1316",
            "USER_RX": "08590f7e-db05-467e-8757-72f6faeb1326",
            "PAIRING": "08590f7e-db05-467e-8757-72f6faeb13e5",
        }
        self.devices = []

        print("scanning for 5 seconds, please wait...")
        adapters = simplepyble.Adapter.get_adapters()

        if len(adapters) == 0:
            print("No adapters found")
            exit()
        adapter = adapters[0]

        adapter.set_callback_on_scan_found(self.scan_found_callback)

        # Scan for 5 seconds
        # with SuppressStdout():
        adapter.scan_start()
        print("Scanning...", end='')
        while len(self.devices) == 0:
            time.sleep(0.5)
            print(".", end='', flush=True)
        print("")
        adapter.scan_stop()
        peripherals = adapter.scan_get_results()

        peripherals = [peripheral for peripheral in peripherals if "VEX_V5" in peripheral.identifier()]
        peripherals = sorted(peripherals, key=lambda peripheral: peripheral.rssi())

        self.peripheral = peripherals[0]

        self.peripheral.connect()

        magic = self.peripheral.read(self.UUIDs["SERVICE"], self.UUIDs["PAIRING"])
        if int.from_bytes(magic, "big") != 0xdeadface:
            print("No V5 Devices Found")
            exit()

        self.peripheral.write_request(self.UUIDs["SERVICE"], self.UUIDs["PAIRING"], bytes([0xff, 0xff, 0xff, 0xff]))

        # Send pairing code
        pairing_bytes = bytes(int(c) for c in "4600")

        self.peripheral.write_request(self.UUIDs["SERVICE"], self.UUIDs["PAIRING"], pairing_bytes)
        print("Sent pairing code")

        cresp = bytes([])
        while cresp != pairing_bytes:
            cresp = self.peripheral.read(self.UUIDs["SERVICE"], self.UUIDs["PAIRING"])

        self.peripheral.notify(self.UUIDs["SERVICE"], self.UUIDs["DATA_TX"], self.handle_notification)

        self.buffer: bytearray = bytearray()

    def scan_found_callback(self, peripheral):
        if "VEX_V5" in peripheral.identifier():
            self.devices.append(peripheral.identifier())

    def handle_notification(self, data):
        # print("Notification received: ", data)
        self.buffer.extend(data)

    def read(self, n_bytes: int = 0) -> bytes:
        if n_bytes <= 0:
            msg = bytes(self.buffer)
            self.buffer = bytearray()
            return msg
        else:
            if len(self.buffer) < n_bytes:
                msg = bytes(self.buffer)
                self.buffer = bytearray()
            else:
                msg, self.buffer = bytes(self.buffer[:n_bytes]), self.buffer[n_bytes:]
            return msg

    def write(self, data: Union[str, bytes]):
        # for line in traceback.format_stack():
        #     print(line.strip())
        if isinstance(data, str):
            data = data.encode(encoding='ascii')
        else:
            data = bytes(data)
        for i in range(0, len(data), MAX_PACKET_SIZE):
            # print(len(data[i:min(len(data), i+MAX_PACKET_SIZE)]))
            self.peripheral.write_command(self.UUIDs["SERVICE"], self.UUIDs["DATA_RX"],
                                          data[i:min(len(data), i + MAX_PACKET_SIZE)])
            # time.sleep(0.3)
        # self.peripheral.write_command(self.UUIDs["SERVICE"], self.UUIDs["DATA_RX"], bytes([0x00]))

    def destroy(self):
        logger(__name__).debug(f'Destroying {self.__class__.__name__} to {self.serial.name}')
        self.peripheral.disconnect()

    @property
    def name(self) -> str:
        return self.serial.portstr

    def __str__(self):
        return str("Bluetooth Port")