import codecs
import os
from proscli.utils import debug
import serial
import signal
import sys
import time
import threading

# This file is a modification of the miniterm implementation on pyserial


class ConsoleBase(object):
    """OS abstraction for console (input/output codec, no echo)"""

    def __init__(self):
        if sys.version_info >= (3, 0):
            self.byte_output = sys.stdout.buffer
        else:
            self.byte_output = sys.stdout
        self.output = sys.stdout

    def setup(self):
        """Set console to read single characters, no echo"""

    def cleanup(self):
        """Restore default console settings"""

    def getkey(self):
        """Read a single key from the console"""
        return None

    def write_bytes(self, byte_string):
        """Write bytes (already encoded)"""
        self.byte_output.write(byte_string)
        self.byte_output.flush()

    def write(self, text):
        """Write string"""
        self.output.write(text)
        self.output.flush()

    def cancel(self):
        """Cancel getkey operation"""

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # context manager:
    # switch terminal temporary to normal mode (e.g. to get user input)

    def __enter__(self):
        self.cleanup()
        return self

    def __exit__(self, *args, **kwargs):
        self.setup()


if os.name == 'nt':  # noqa
    import msvcrt
    import ctypes

    class Out(object):
        """file-like wrapper that uses os.write"""

        def __init__(self, fd):
            self.fd = fd

        def flush(self):
            pass

        def write(self, s):
            os.write(self.fd, s)

    class Console(ConsoleBase):
        def __init__(self):
            super(Console, self).__init__()
            self._saved_ocp = ctypes.windll.kernel32.GetConsoleOutputCP()
            self._saved_icp = ctypes.windll.kernel32.GetConsoleCP()
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
            self.output = codecs.getwriter('UTF-8')(Out(sys.stdout.fileno()),
                                                    'replace')
            # the change of the code page is not propagated to Python,
            # manually fix it
            sys.stderr = codecs.getwriter('UTF-8')(Out(sys.stderr.fileno()),
                                                   'replace')
            sys.stdout = self.output
            self.output.encoding = 'UTF-8'  # needed for input

        def __del__(self):
            ctypes.windll.kernel32.SetConsoleOutputCP(self._saved_ocp)
            ctypes.windll.kernel32.SetConsoleCP(self._saved_icp)

        def getkey(self):
            while True:
                z = msvcrt.getwch()
                if z == chr(13):
                    return chr(10)
                elif z in (chr(0), chr(0x0e)):    # functions keys, ignore
                    msvcrt.getwch()
                else:
                    return z

        def cancel(self):
            # CancelIo, CancelSynchronousIo do not seem to work when using
            # getwch, so instead, send a key to the window with the console
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            ctypes.windll.user32.PostMessageA(hwnd, 0x100, 0x0d, 0)

elif os.name == 'posix':
    import atexit
    import termios
    import select

    class Console(ConsoleBase):
        def __init__(self):
            super(Console, self).__init__()
            self.fd = sys.stdin.fileno()
            # an additional pipe is used in getkey, so that the cancel method
            # can abort the waiting getkey method
            self.pipe_r, self.pipe_w = os.pipe()
            self.old = termios.tcgetattr(self.fd)
            atexit.register(self.cleanup)
            if sys.version_info < (3, 0):
                self.enc_stdin = codecs.\
                                 getreader(sys.stdin.encoding)(sys.stdin)
            else:
                self.enc_stdin = sys.stdin

        def setup(self):
            new = termios.tcgetattr(self.fd)
            new[3] = new[3] & ~termios.ICANON & ~termios.ECHO & ~termios.ISIG
            new[6][termios.VMIN] = 1
            new[6][termios.VTIME] = 0
            termios.tcsetattr(self.fd, termios.TCSANOW, new)

        def getkey(self):
            ready, _, _ = select.select([self.enc_stdin, self.pipe_r], [],
                                        [], None)
            if self.pipe_r in ready:
                os.read(self.pipe_r, 1)
                return
            c = self.enc_stdin.read(1)
            if c == chr(0x7f):
                c = chr(8)    # map the BS key (which yields DEL) to backspace
            return c

        def cancel(self):
            os.write(self.pipe_w, b"x")

        def cleanup(self):
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old)

else:
    raise NotImplementedError(
        'Sorry no implementation for your platform ({})'
        ' available.'.format(sys.platform))


class Terminal(object):
    """This class is loosely based off of the pyserial miniterm"""
    def __init__(self, serial_instance: serial.Serial, transformations=(),
                 output_raw=False):
        self.serial = serial_instance
        self.transformations = transformations
        self._reader_alive = None
        self.receiver_thread = None
        self._transmitter_alive = None
        self.transmitter_thread = None
        self.alive = None
        self.output_raw = output_raw
        self.no_sigint = True  # SIGINT flag
        signal.signal(signal.SIGINT, self.catch_sigint)  # SIGINT handler
        self.console = Console()

    def _start_rx(self):
        self._reader_alive = True
        self.receiver_thread = threading.Thread(target=self.reader,
                                                name='serial-rx-term')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_rx(self):
        self._reader_alive = False
        if hasattr(self.serial, 'cancel_read'):
            self.serial.cancel_read()
        self.receiver_thread.join()

    def _start_tx(self):
        self._transmitter_alive = True
        self.transmitter_thread = threading.Thread(target=self.transmitter,
                                                   name='serial-tx-term')
        self.transmitter_thread.daemon = True
        self.transmitter_thread.start()

    def _stop_tx(self):
        self._transmitter_alive = False
        if hasattr(self.serial, 'cancel_write'):
            self.serial.cancel_write()
        self.transmitter_thread.join()

    def reader(self):
        start_time = time.clock
        try:
            while self.alive and self._reader_alive:
                data = self.serial.read(self.serial.in_waiting or 1)
                if data:
                    if self.output_raw:
                        self.console.write_bytes(data)
                    else:
                        text = data.decode('utf-8', 'ignore')
                        for transformation in self.transformations:
                            text = transformation(text)
                        self.console.write(text)
        except serial.SerialException as e:
            debug(e)
            self.alive = False

    def transmitter(self):
        try:
            while self.alive and self._transmitter_alive:
                try:
                    c = self.console.getkey()
                except KeyboardInterrupt:
                    c = '\x03'
                if not self.alive:
                    break
                if c == '\x03' or not self.no_sigint:
                    self.stop()
                    break
                else:
                    self.serial.write(c.encode('utf-8'))
                    self.console.write(c)
        except Exception as e:
            debug(e)
            self.alive = False

    def catch_sigint(self):
        self.no_sigint = False

    def start(self):
        self.alive = True
        self._start_rx()
        self._start_tx()

    def join(self):
        if self.transmitter_thread.is_alive():
            self.transmitter_thread.join()
        if self.receiver_thread.is_alive():
            self.receiver_thread.join()

    def stop(self):
        print('Stopping terminal!')
        self.alive = False
        self._stop_rx()
        self._stop_tx()
