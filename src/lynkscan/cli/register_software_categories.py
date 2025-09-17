"""Register software categories from a JSON file."""

import json
import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import List

from sqlmodel import Session
from sqlmodel import create_engine
from sqlmodel import select

from lynkscan.db.manager import DatabaseManager
from lynkscan.db.models import SoftwareCategory

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
parser = ArgumentParser(
    description="Register software categories from a JSON file."
)
parser.add_argument(
    "--input",
    "-i",
    type=str,
    required=True,
    help="Input JSON file with software categories",
)
parser.add_argument(
    "--engine-url",
    "-e",
    type=str,
    default="sqlite:///lynkscan.db",
    help="Database engine URL, e.g., sqlite:///lynkscan.db or postgresql",
)


def run_register_software_categories() -> None:
    """Run the register_software_categories script."""
    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file does not exist: {args.input}")
        return

    with open(input_path, "r", encoding="utf-8") as fin:
        data = json.load(fin)
        categories = data.get("categories", [])
        software_categories = [
            SoftwareCategory.model_validate(cat) for cat in categories
        ]

    db_manager = DatabaseManager(engine_url=args.engine_url)
    session = db_manager.get_session_instance()
    repo = db_manager.software_category(session)
    for category in software_categories:
        software_category = SoftwareCategory(name=category.name)
        repo.create(software_category)
        logger.info(f"Registered category: {category.name}")
