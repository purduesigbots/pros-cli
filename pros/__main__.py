"""PROS CLI."""

import ctypes
import sys

import rich_click as click

if sys.platform == "win32":  # Enables ANSI color codes in Windows consoles
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


@click.command("pros")
def pros() -> None:
    """Root CLI command."""
    click.echo("Hello, World!")
