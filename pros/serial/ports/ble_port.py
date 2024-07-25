import asyncio

import click
import simplepyble as ble

from typing import *
import time

from pros.common import logger
from pros.serial.ports.exceptions import ConnectionRefusedException, PortNotFoundException
from base_port import BasePort, PortConnectionException

MAX_PACKET_SIZE = 244

V5_SERVICE = "0x08590f7e_db05_467e_8757_72f6faeb13d5"

CHARACTERISTIC_SYSTEM_TX = "0x08590f7e_db05_467e_8757_72f6faeb1306"
CHARACTERISTIC_SYSTEM_RX = "0x08590f7e_db05_467e_8757_72f6faeb13f5"

CHARACTERISTIC_USER_TX = "0x08590f7e_db05_467e_8757_72f6faeb1316"
CHARACTERISTIC_USER_RX = "0x08590f7e_db05_467e_8757_72f6faeb1326"

CHARACTERISTIC_PAIRING = "0x08590f7e_db05_467e_8757_72f6faeb13e5"

UNPAIRED_MAGIC = 0xdeadface


async def find_device(scan_time: time, max_devices_count: int) -> list[ble.Peripheral]:
    devices = []
    adapters: List[ble.Adapter] = ble.Adapter.get_adapters()

    if len(adapters) == 0:
        print("No adapters found")
        return None
    adapter = adapters[0]

    def device_found_or_updated_callback(peripheral: ble.Peripheral):
        logger(__name__).debug(f"Discovered device: {peripheral}")
        if V5_SERVICE in peripheral.address() and peripheral.is_connectable():
            devices.append(peripheral)
            if len(devices) >= max_devices_count:
                adapter.stop_scan()

    adapter.set_callback_on_scan_start(lambda: logger(__name__).info("Scanning started"))
    adapter.set_callback_on_scan_found(device_found_or_updated_callback)
    adapter.set_callback_on_scan_updated(device_found_or_updated_callback)
    adapter.set_callback_on_scan_stop(lambda: logger(__name__).info("Scanning complete"))

    # exit when max_devices_count is reached or scan_time is reached
    adapter.scan_for(scan_time)

    # sort devices by signal strength(strongest to weakest)
    devices = sorted(devices, key=lambda device: device.rssi(), reverse=True)
    print(f"Discovered {len(devices)} devices: {devices}")

    logger(__name__).info(f"Discovered {len(devices)} devices: {devices}")

    return devices


class BlePort(BasePort):
    def __init__(self, name: str, peripheral: ble.Peripheral):
        self.name = name
        self.peripheral = peripheral

        self.pairing()
        self.buffer: bytearray = bytearray()

        self.peripheral.notify(V5_SERVICE, CHARACTERISTIC_SYSTEM_TX, self.on_notify)

    @staticmethod
    async def create_ble_port(self, peripheral: ble.Peripheral):
        system_rx_validate = False
        system_tx_validate = False
        user_rx_validate = False
        user_tx_validate = False
        pairing_validate = False

        for service in peripheral.services():
            for characteristic in service.characteristics():
                service_id = service.uuid()
                if service_id == V5_SERVICE:
                    character_id = characteristic.uuid()
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

    async def pairing(self):
        if not await self.peripheral.is_connected():
            await self.peripheral.connect()
            magic = self.peripheral.read(V5_SERVICE, CHARACTERISTIC_PAIRING)
            if int.from_bytes(magic, "big") != UNPAIRED_MAGIC:
                logger(__name__).warning("Unable to pair with peripheral")
                exit()
            else:
                self.peripheral.write_request(V5_SERVICE, CHARACTERISTIC_PAIRING,
                                              bytes([0xff, 0xff, 0xff, 0xff]))

                # Request pairing code from user
                code = click.prompt("Enter the pairing code(4 digits): ", type=int)
                pairing_code = bytes(code)
                self.peripheral.write_request(V5_SERVICE, CHARACTERISTIC_PAIRING, pairing_code)

                # Wait for peripheral to send acknowledgement
                read_ack = self.peripheral.read(V5_SERVICE, CHARACTERISTIC_PAIRING)
                if read_ack != pairing_code:
                    logger(__name__).warning("Pairing failed")
                    exit()

                logger(__name__).info("Pairing successful")

        else:
            raise ConnectionRefusedException(self.name, Exception("Peripheral is already connected"))

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

    @property
    def name(self) -> str:
        return self.name

    def __str__(self):
        return str("Bluetooth Port")

if __name__ == "__main__":
    asyncio.run(find_device(5000, 2))
    pass