"""Interactive mode for the LynkScan CLI application."""

from lynkscan.cli.user_interface import TextInterface
from lynkscan.utils import GitVersion


def run_interactive_mode():
    """Run the interactive mode of the LynkScan CLI application."""
    TextInterface.print_banner(version=GitVersion.version())
