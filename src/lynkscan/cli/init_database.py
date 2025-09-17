"""Initializing database."""

from argparse import ArgumentParser

from lynkscan.db.manager import DatabaseManager

parser = ArgumentParser(description="Initialize the database.")
parser.add_argument(
    "--engine-url",
    "-e",
    type=str,
    default="sqlite:///lynkscan.db",
    help="Database engine URL, e.g., sqlite:///lynkscan.db or postgresql",
)


def run_init_database() -> None:
    """Initialize the database and create tables."""
    args = parser.parse_args()
    db_manager = DatabaseManager(args.engine_url)
    db_manager.create_db_and_tables()
