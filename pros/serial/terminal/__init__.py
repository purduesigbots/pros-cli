import serial
import signal
import time
import pros.serial.terminal.serial_terminal


def display_terminal(port: serial.Serial):
    term = pros.serial.terminal.serial_terminal.Terminal(port)
    signal.signal(signal.SIGINT, term.stop)
    term.start()
    while term.alive:
        time.sleep(0.01)
    term.join()