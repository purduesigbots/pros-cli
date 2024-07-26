import asyncio

import click
import simplepyble as ble

from typing import *
import time

from pros.common import logger
from pros.serial.ports.exceptions import ConnectionRefusedException, PortNotFoundException
from base_port import BasePort, PortConnectionException

MAX_PACKET_SIZE = 244

V5_SERVICE = "08590f7e-db05-467e-8757-72f6faeb13d5"

CHARACTERISTIC_SYSTEM_TX = "08590f7e-db05-467e-8757-72f6faeb1306"
CHARACTERISTIC_SYSTEM_RX = "08590f7e-db05-467e-8757-72f6faeb13f5"

CHARACTERISTIC_USER_TX = "08590f7e-db05-467e-8757-72f6faeb1316"
CHARACTERISTIC_USER_RX = "08590f7e-db05-467e-8757-72f6faeb1326"

CHARACTERISTIC_PAIRING = "08590f7e-db05-467e-8757-72f6faeb13e5"

UNPAIRED_MAGIC = 0xdeadface


def find_device(scan_time: time, max_devices_count: int) -> list[ble.Peripheral]:
    devices = []
    adapters: List[ble.Adapter] = ble.Adapter.get_adapters()

    if len(adapters) == 0:
        print("No adapters found")
        pass
    adapter = adapters[0]

    def device_found_or_updated_callback(peripheral: ble.Peripheral):
        print(f"Discovered device {peripheral.identifier()}")
        logger(__name__).debug(f"Discovered device: {peripheral}")
        # if "V5" in peripheral.identifier() and len(peripheral.services()) > 1:
        #     print(peripheral.services()[2].uuid())

        for service in peripheral.services():
            if service.uuid() == V5_SERVICE:
                devices.append(peripheral)
                if len(devices) >= max_devices_count:
                    adapter.stop_scan()

    adapter.set_callback_on_scan_start(lambda: logger(__name__).info("Scanning started"))
    adapter.set_callback_on_scan_found(device_found_or_updated_callback)
    # adapter.set_callback_on_scan_updated(device_found_or_updated_callback)
    adapter.set_callback_on_scan_stop(lambda: logger(__name__).info("Scanning complete"))

    # exit when max_devices_count is reached or scan_time is reached
    adapter.scan_for(scan_time)

    # sort devices by signal strength(strongest to weakest)
    devices = sorted(devices, key=lambda device: device.rssi(), reverse=True)
    print(f"Discovered {len(devices)} devices: {devices}")

    logger(__name__).info(f"Discovered {len(devices)} devices: {devices}")

    return devices


class BlePort(BasePort):
    @property
    def name(self):
        return self._name

    def __init__(self, name: str, peripheral: ble.Peripheral):
        self.name = name
        self.peripheral = peripheral
        self.buffer: bytearray = bytearray()
        self.pairing()

        try:
            self.peripheral.notify(V5_SERVICE, CHARACTERISTIC_SYSTEM_TX, self.on_notify)
        except Exception as e:
            pass

    @staticmethod
    def create_ble_port(peripheral: ble.Peripheral):
        system_rx_validate = False
        system_tx_validate = False
        user_rx_validate = False
        user_tx_validate = False
        pairing_validate = False

        if not peripheral.is_connected():
            peripheral.connect()

        print(f"{len(peripheral.services())}")
        for service in peripheral.services():
            service_id = service.uuid()
            # if service_id == V5_SERVICE:
            print(f"{len(service.characteristics())}")
            for characteristic in service.characteristics():
                character_id = characteristic.uuid()
                print(f"{service_id}: {characteristic.uuid()}")
                if character_id == CHARACTERISTIC_SYSTEM_RX:
                    system_rx_validate = True
                elif character_id == CHARACTERISTIC_SYSTEM_TX:
                    system_tx_validate = True
                elif character_id == CHARACTERISTIC_USER_RX:
                    user_rx_validate = True
                elif character_id == CHARACTERISTIC_USER_TX:
                    user_tx_validate = True
                elif character_id == CHARACTERISTIC_PAIRING:
                    pairing_validate = True

        if not system_rx_validate or \
                not system_tx_validate or \
                not user_rx_validate or \
                not user_tx_validate or \
                not pairing_validate:
            raise PortConnectionException(f"Could not find all required characteristics on {peripheral.identifier()}")

        return BlePort(peripheral.identifier(), peripheral)

    def pairing(self):

        magic = self.peripheral.read(V5_SERVICE, CHARACTERISTIC_PAIRING)
        if int.from_bytes(magic, "big") != UNPAIRED_MAGIC:
            logger(__name__).info("Already paired")
            print("Already paired")
            pass
        else:
            # request showing pairing code on the brain screen
            self.peripheral.write_request(V5_SERVICE, CHARACTERISTIC_PAIRING,
                                          bytes([0xff, 0xff, 0xff, 0xff]))

            # Request pairing code from user
            code: str = click.prompt("Enter the pairing code(4 digits)", type=str)
            # print(code)
            pairing_code: bytes = bytes(int(c) for c in code)
            # print(f"pairing bytes: {pairing_code.__str__()}")
            self.peripheral.write_request(V5_SERVICE, CHARACTERISTIC_PAIRING, pairing_code)

            # Wait for peripheral to send acknowledgement
            read_ack = bytes([])
            while read_ack != pairing_code:
                read_ack = self.peripheral.read(V5_SERVICE, CHARACTERISTIC_PAIRING)
                # print(read_ack.__str__())
                # print("Pairing failed")
                # logger(__name__).warning("Pairing failed")
                # exit()

            print("Pairing successful")
            logger(__name__).info("Pairing successful")

    def on_notify(self, data: bytes):
        self.buffer.extend(data)

    def write(self, data: bytes):
        if self.peripheral.is_paired():
            raise PortNotFoundException(self.name, Exception("Peripheral is not paired"))

        for i in range(0, len(data), MAX_PACKET_SIZE):
            self.peripheral.write_command(V5_SERVICE, CHARACTERISTIC_SYSTEM_RX,
                                          data[i:min(len(data), i + MAX_PACKET_SIZE)])

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

    def read_all(self) -> bytes:
        return self.read()

    def destroy(self):
        logger(__name__).debug(f'Destroying {self.__class__.__str__} to {self.name}')
        self.peripheral.disconnect()
        pass

    def __str__(self):
        return str("Bluetooth Port")

    @name.setter
    def name(self, value):
        self._name = value


if __name__ == "__main__":
    # test this first
    p_list = find_device(5000, 2)
    ble = BlePort.create_ble_port(p_list[0])
    time.sleep(5)
    ble.destroy()
    pass
