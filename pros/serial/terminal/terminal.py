import signal
import threading

import colorama

from pros.common.utils import logger
from pros.serial import decode_bytes_to_str
from pros.serial.devices import StreamDevice
from pros.serial.ports import PortConnectionException
from .console import Console


# This file is a modification of the miniterm implementation on pyserial


class Terminal(object):
    """This class is loosely based off of the pyserial miniterm"""

    def __init__(self, port_instance: StreamDevice, transformations=(),
                 output_raw: bool = False, request_banner: bool = True):
        self.device = port_instance
        self.device.subscribe(b'sout')
        self.device.subscribe(b'serr')
        self.transformations = transformations
        self._reader_alive = None
        self.receiver_thread = None  # type: threading.Thread
        self._transmitter_alive = None
        self.transmitter_thread = None  # type: threading.Thread
        self.alive = threading.Event()  # type: threading.Event
        self.output_raw = output_raw
        self.request_banner = request_banner
        self.no_sigint = True  # SIGINT flag
        signal.signal(signal.SIGINT, self.catch_sigint)  # SIGINT handler
        self.console = Console()
        self.console.output = colorama.AnsiToWin32(self.console.output).stream

    def _start_rx(self):
        self._reader_alive = True
        self.receiver_thread = threading.Thread(target=self.reader,
                                                name='serial-rx-term')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_rx(self):
        self._reader_alive = False
        self.receiver_thread.join()

    def _start_tx(self):
        self._transmitter_alive = True
        self.transmitter_thread = threading.Thread(target=self.transmitter,
                                                   name='serial-tx-term')
        self.transmitter_thread.daemon = True
        self.transmitter_thread.start()

    def _stop_tx(self):
        self.console.cancel()
        self._transmitter_alive = False
        self.transmitter_thread.join()

    def reader(self):
        if self.request_banner:
            try:
                self.device.write(b'pRb')
            except Exception as e:
                logger(__name__).exception(e)
        try:
            while not self.alive.is_set() and self._reader_alive:
                data = self.device.read()
                if not data:
                    continue
                if data[0] == b'sout':
                    text = decode_bytes_to_str(data[1])
                elif data[0] == b'serr':
                    text = '{}{}{}'.format(colorama.Fore.RED, decode_bytes_to_str(data[1]), colorama.Style.RESET_ALL)
                elif data[0] == b'kdbg':
                    text = '{}\n\nKERNEL DEBUG:\t{}{}\n'.format(colorama.Back.GREEN + colorama.Style.BRIGHT,
                                                                decode_bytes_to_str(data[1]),
                                                                colorama.Style.RESET_ALL)
                elif data[0] != b'':
                    text = '{}{}'.format(decode_bytes_to_str(data[0]), decode_bytes_to_str(data[1]))
                else:
                    text = "{}".format(decode_bytes_to_str(data[1]))
                self.console.write(text)
        except UnicodeError as e:
            logger(__name__).exception(e)
        except PortConnectionException:
            logger(__name__).warning(f'Connection to {self.device.name} broken')
            if not self.alive.is_set():
                self.stop()
        except Exception as e:
            if not self.alive.is_set():
                logger(__name__).exception(e)
            else:
                logger(__name__).debug(e)
            self.stop()
        logger(__name__).info('Terminal receiver dying')

    def transmitter(self):
        try:
            while not self.alive.is_set() and self._transmitter_alive:
                try:
                    c = self.console.getkey()
                except KeyboardInterrupt:
                    c = '\x03'
                if self.alive.is_set():
                    break
                if c == '\x03' or not self.no_sigint:
                    self.stop()
                    break
                else:
                    self.device.write(c.encode(encoding='utf-8'))
                    self.console.write(c)
        except Exception as e:
            if not self.alive.is_set():
                logger(__name__).exception(e)
            else:
                logger(__name__).debug(e)
            self.stop()
        logger(__name__).info('Terminal transmitter dying')

    def catch_sigint(self):
        self.no_sigint = False

    def start(self):
        self.alive.clear()
        self._start_rx()
        self._start_tx()

    # noinspection PyUnusedLocal
    def stop(self, *args):
        if not self.alive.is_set():
            logger(__name__).warning('Stopping terminal')
            self.alive.set()
            self.device.destroy()
            if threading.current_thread() != self.transmitter_thread and self.transmitter_thread.is_alive():
                self.console.cleanup()
                self.console.cancel()
            logger(__name__).info('All done!')

    def join(self):
        try:
            if self.receiver_thread.is_alive():
                self.receiver_thread.join()
            if self.transmitter_thread.is_alive():
                self.transmitter_thread.join()
        except:
            self.stop()
