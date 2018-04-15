import struct
import threading
from collections import defaultdict
from typing import *
from queue import Queue

import msgpack

from pros.common import logger
from pros.serial.application import Application
from pros.serial.devices import StreamDevice
from .schema import JinxSchema


class JinxApplication(Application):
    def __init__(self, device: StreamDevice):
        super().__init__(device)
        device.subscribe(b'jinx')
        self.transmitter_thread: threading.Thread = None
        self.receiver_thread: threading.Thread = None
        self.alive: threading.Event = threading.Event()
        self.schemas: Dict[int, JinxSchema] = {}
        self.deferred: Dict[int, List[Tuple[int, bytes]]] = defaultdict(list)
        self.queue: Queue = Queue()

    def get_jinx_data(self):
        topic, data = self.device.read()
        while topic != b'jinx':
            topic, data = self.device.read()
        return data

    def parse_value_messages(self, data: bytes) -> Iterable[Tuple[str, int, Iterable]]:
        base_timestamp, data = struct.unpack('L', data[:4])[0], bytearray(data[4:])
        keys = self.schemas.keys()
        yield ('__pros_kernel_time', base_timestamp, base_timestamp)
        while len(data) > 0:
            size, time_offset, jinx_id = struct.unpack('BBH', data[:4])
            data = data[4:]
            if jinx_id in keys:
                schema = self.schemas[jinx_id]
                yield (schema.name, base_timestamp + time_offset, schema.transform(data[:size]))
            else:
                self.deferred[jinx_id].append((base_timestamp + time_offset, data[:size]))
            data = data[size:]

    @staticmethod
    def create_update_message(values: Iterable[Tuple[str, int, Iterable]]):
        message: Dict[str, Dict[str, List]] = defaultdict(lambda: {'time': [], 'data': []})
        for value in values:
            message[value[0]]['time'].append(value[1])
            message[value[0]]['data'].append(value[2])
        return dict(message)

    def tx_loop(self):
        while not self.alive.is_set():
            data = self.get_jinx_data()
            if data[0] == b'S'[0]:
                schema = {k: JinxSchema(**v) for k, v in msgpack.unpackb(data[1:], raw=False).items()}
                self.schemas.update(schema)
                keys = self.schemas.keys()
                for jinx_id, values in self.deferred.items():
                    if jinx_id in keys:
                        schema = self.schemas[jinx_id]
                        self.queue.put(self.create_update_message([(schema.name, t, schema.transform(v)) for (t, v) in values]))
                self.deferred = defaultdict(list)
            elif data[0] == b'D'[0]:
                values = self.parse_value_messages(data[1:])
                self.queue.put(self.create_update_message(values))
            else:
                logger(__name__).warning(f'Unknown message type {data[0:1].decode()}')

    def start(self):
        self.alive.clear()
        self.transmitter_thread = threading.Thread(target=self.tx_loop, name='jinx-tx-loop')
        self.transmitter_thread.daemon = True
        self.transmitter_thread.start()

    def stop(self):
        pass

    def join(self):
        try:
            if self.receiver_thread.is_alive():
                self.receiver_thread.join()
            if self.transmitter_thread.is_alive():
                self.transmitter_thread.join()
        except:
            self.stop()
