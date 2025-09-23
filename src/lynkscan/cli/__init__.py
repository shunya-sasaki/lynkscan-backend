"""CLI commands for LynkScan."""

from lynkscan.cli.fetch_license_info import run_fetch_license_info
from lynkscan.cli.init_database import run_init_database
from lynkscan.cli.register_github_repo import run as run_register_github_repo
from lynkscan.cli.register_license import run_register_license
from lynkscan.cli.register_license_categories import (
    run_register_license_categories,
)
from lynkscan.cli.register_software_categories import (
    run_register_software_categories,
)

__all__ = [
    "run_fetch_license_info",
    "run_init_database",
    "run_register_software_categories",
    "run_register_license_categories",
    "run_register_license",
    "run_register_github_repo",
]
