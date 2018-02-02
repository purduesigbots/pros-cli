from .base_port import BasePort
from .serial_share_bridge import *


class SerialSharePort(BasePort):
    def __init__(self, port_name: str, topic: bytes = b'sout', addr: str = '127.0.0.1',
                 to_device_port: int = None, from_device_port: int = None):
        self.port_name = port_name
        self.topic = topic
        self._base_addr = addr
        self._to_port_num = to_device_port
        self._from_port_num = from_device_port

        if self._to_port_num is None:
            self._to_port_num = get_to_device_port_num(self.port_name)
        if self._from_port_num is None:
            self._from_port_num = get_from_device_port_num(self.port_name)

        server = SerialShareBridge(self.port_name, self._base_addr, self._to_port_num, self._from_port_num)
        server.start()

        self.ctx = zmq.Context()  # type: zmq.Context

        self.from_device_sock = self.ctx.socket(zmq.SUB)  # type: zmq.Socket
        self.from_device_sock.setsockopt(zmq.SUBSCRIBE, self.topic)
        self.from_device_sock.setsockopt(zmq.SUBSCRIBE, b'kdbg')
        self.from_device_sock.connect('tcp://{}:{}'.format(self._base_addr, self._from_port_num))
        logger(__name__).info(
            'Connected from device as a subscriber on tcp://{}:{}'.format(self._base_addr, self._from_port_num))

        self.to_device_sock = self.ctx.socket(zmq.PUB)  # type: zmq.Socket
        self.to_device_sock.connect('tcp://{}:{}'.format(self._base_addr, self._to_port_num))
        logger(__name__).info(
            'Connected to device as a publisher on tcp://{}:{}'.format(self._base_addr, self._to_port_num))

        self.alive = threading.Event()
        self.watchdog_thread = threading.Thread(target=self._kick_watchdog, name='Client Kicker')
        self.watchdog_thread.start()

    def read(self, n_bytes: int = -1):
        if n_bytes <= 0:
            n_bytes = 1
        data = bytearray()
        for _ in range(n_bytes):
            data.extend(self.from_device_sock.recv_multipart()[1])
        return bytes(data)

    def read_packet(self):
        return self.from_device_sock.recv_multipart()

    def write(self, data: AnyStr):
        if isinstance(data, str):
            data = data.encode(encoding='ascii')
        assert isinstance(data, bytes)
        self.to_device_sock.send_multipart([b'send', data])

    def subscribe(self, topic: bytes):
        assert len(topic) == 4
        self.write(bytearray([*b'pRe', *topic]))
        self.from_device_sock.subscribe(topic=topic)

    def unsubscribe(self, topic: bytes):
        assert len(topic) == 4
        self.write(bytearray([*b'pRd', *topic]))
        self.from_device_sock.unsubscribe(topic=topic)

    def destroy(self):
        logger(__name__).info('Destroying {}'.format(self))
        self.alive.set()
        if self.watchdog_thread.is_alive():
            self.watchdog_thread.join()
        if not self.from_device_sock.closed:
            self.from_device_sock.close(linger=0)
        if not self.ctx.closed:
            self.ctx.destroy(linger=0)

    def _kick_watchdog(self):
        time.sleep(0.5)
        while not self.alive.is_set():
            logger(__name__).debug('Kicking server from {}'.format(threading.current_thread()))
            self.to_device_sock.send_multipart([b'kick'])
            self.alive.wait(2.5)
        logger(__name__).info('Watchdog kicker is dying')
