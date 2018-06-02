import logging.handlers
import multiprocessing
import threading
import time

import zmq
from cobs import cobs
from pros.common.utils import *

from .direct_port import DirectPort
from .. import bytes_to_str


def get_port_num(serial_port_name: str, hash: str) -> int:
    return sum("Powered by PROS: {}-{}".format(serial_port_name, hash).encode(encoding='ascii'))


def get_from_device_port_num(serial_port_name: str) -> int:
    return get_port_num(serial_port_name, 'from')


def get_to_device_port_num(serial_port_name: str) -> int:
    return get_port_num(serial_port_name, 'to')


class SerialShareBridge(object):
    def __init__(self, serial_port_name: str, base_addr: str = '127.0.0.1',
                 to_device_port_num: int = None, from_device_port_num: int = None):
        self._serial_port_name = serial_port_name
        self._base_addr = base_addr
        if to_device_port_num is None:
            to_device_port_num = get_to_device_port_num(serial_port_name)
        if from_device_port_num is None:
            from_device_port_num = get_from_device_port_num(serial_port_name)
        self._to_port_num = to_device_port_num
        self._from_port_num = from_device_port_num
        self.port = None  # type: SerialPort
        self.zmq_ctx = None  # type: zmq.Context
        self.from_device_thread = None  # type: threading.Thread
        self.to_device_thread = None  # type: threading.Thread
        self.dying = None  # type: threading.Event

    @property
    def to_device_port_num(self):
        return self._to_port_num

    @property
    def from_device_port_num(self):
        return self._from_port_num

    def start(self):
        # this function is still in the parent process
        mp_ctx = multiprocessing.get_context('spawn')
        barrier = multiprocessing.Barrier(3)
        task = mp_ctx.Process(target=self._start, name='Serial Share Bridge', args=(barrier,))
        task.daemon = False
        task.start()
        barrier.wait(1)
        return task

    def kill(self, do_join: bool = False):
        logger(__name__).info('Killing serial share server due to watchdog')
        self.dying.set()
        self.port.destroy()
        if not self.zmq_ctx.closed:
            self.zmq_ctx.destroy(linger=0)
        if do_join:
            if threading.current_thread() != self.from_device_thread and self.from_device_thread.is_alive():
                self.from_device_thread.join()
            if threading.current_thread() != self.to_device_thread and self.to_device_thread.is_alive():
                self.to_device_thread.join()

    def _start(self, initialization_barrier: multiprocessing.Barrier):
        try:
            log_dir = os.path.join(get_pros_dir(), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            pros_logger = logging.getLogger(pros.__name__)
            pros_logger.setLevel(logging.DEBUG)
            log_file_name = os.path.join(get_pros_dir(), 'logs', 'serial-share-bridge.log')
            handler = logging.handlers.TimedRotatingFileHandler(log_file_name, backupCount=1)
            handler.setLevel(logging.DEBUG)
            fmt_str = '%(name)s.%(funcName)s:%(levelname)s - %(asctime)s - %(message)s (%(process)d) ({})' \
                .format(self._serial_port_name)
            handler.setFormatter(logging.Formatter(fmt_str))
            pros_logger.addHandler(handler)

            self.zmq_ctx = zmq.Context()
            # timeout is none, so blocks indefinitely. Helps reduce CPU usage when there's nothing being recv
            self.port = DirectPort(self._serial_port_name, timeout=None)
            self.from_device_thread = threading.Thread(target=self._from_device_loop, name='From Device Reader',
                                                       daemon=False, args=(initialization_barrier,))
            self.to_device_thread = threading.Thread(target=self._to_device_loop, name='To Device Reader',
                                                     daemon=False, args=(initialization_barrier,))
            self.dying = threading.Event()  # type: threading.Event
            self.from_device_thread.start()
            self.to_device_thread.start()

            while not self.dying.wait(10000):
                pass

            logger(__name__).info('Main serial share bridge thread is dying. Everything else should be dead: {}'.format(
                threading.active_count() - 1))
            self.kill(do_join=True)
        except Exception as e:
            initialization_barrier.abort()
            logger(__name__).exception(e)

    def _from_device_loop(self, initialization_barrier: multiprocessing.Barrier):
        errors = 0
        rxd = 0
        try:
            from_ser_sock = self.zmq_ctx.socket(zmq.PUB)
            addr = 'tcp://{}:{}'.format(self._base_addr, self._from_port_num)
            from_ser_sock.bind(addr)
            logger(__name__).info('Bound from device broadcaster as a publisher to {}'.format(addr))
            initialization_barrier.wait()
            buffer = bytearray()
            while not self.dying.is_set():
                try:
                    # read one byte as a blocking call so that we aren't just polling which sucks up a lot of CPU,
                    # then read everything available
                    buffer.extend(self.port.read(1))
                    buffer.extend(self.port.read(-1))
                    while b'\0' in buffer and not self.dying.is_set():
                        msg, buffer = buffer.split(b'\0', 1)
                        msg = cobs.decode(msg)
                        from_ser_sock.send_multipart((msg[:4], msg[4:]))
                        rxd += 1
                    time.sleep(0)
                except Exception as e:
                    # TODO: when getting a COBS decode error, rebroadcast the bytes on sout
                    logger(__name__).error('Unexpected error handling {}'.format(bytes_to_str(msg[:-1])))
                    logger(__name__).exception(e)
                    errors += 1
                    logger(__name__).info('Current from device broadcasting error rate: {} errors. {} successful. {}%'
                                          .format(errors, rxd, errors / (errors + rxd)))
        except Exception as e:
            initialization_barrier.abort()
            logger(__name__).exception(e)
        logger(__name__).warning('From Device Broadcaster is dying now.')
        logger(__name__).info('Current from device broadcasting error rate: {} errors. {} successful. {}%'
                              .format(errors, rxd, errors / (errors + rxd)))
        try:
            self.kill(do_join=False)
        except:
            sys.exit(0)

    def _to_device_loop(self, initialization_barrier: multiprocessing.Barrier):
        try:
            to_ser_sock = self.zmq_ctx.socket(zmq.SUB)
            addr = 'tcp://{}:{}'.format(self._base_addr, self._to_port_num)
            to_ser_sock.bind(addr)
            to_ser_sock.setsockopt(zmq.SUBSCRIBE, b'')
            logger(__name__).info('Bound to device broadcaster as a subscriber to {}'.format(addr))
            watchdog = threading.Timer(10, self.kill)
            initialization_barrier.wait()
            watchdog.start()
            while not self.dying.is_set():
                msg = to_ser_sock.recv_multipart()
                if not msg or self.dying.is_set():
                    continue
                if msg[0] == b'kick':
                    logger(__name__).debug('Kicking watchdog on server {}'.format(threading.current_thread()))
                    watchdog.cancel()
                    watchdog = threading.Timer(msg[1][1] if len(msg) > 1 and len(msg[1]) > 0 else 5, self.kill)
                    watchdog.start()
                elif msg[0] == b'send':
                    logger(self).debug('Writing {} to {}'.format(bytes_to_str(msg[1]), self.port.port_name))
                    self.port.write(msg[1])
        except Exception as e:
            initialization_barrier.abort()
            logger(__name__).exception(e)
        logger(__name__).warning('To Device Broadcaster is dying now.')
        try:
            self.kill(do_join=False)
        except:
            sys.exit(0)
