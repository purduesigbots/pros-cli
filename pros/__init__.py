"""PROS CLI."""

import ctypes
import sys

__all__ = [
    "conductor",
    "pros",
]

from pros.cli import pros
from pros.conductor import conductor

if sys.platform == "win32":  # Enables ANSI color codes in Windows consoles
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
