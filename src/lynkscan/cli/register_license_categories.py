"""Register license categories from a JSON file."""

import json
import logging
from argparse import ArgumentParser
from pathlib import Path

from lynkscan.db.manager import DatabaseManager
from lynkscan.db.models import LicenseCategory
from lynkscan.models import AppConfig
from lynkscan.utils import CustomLogger

parser = ArgumentParser(
    description="Register license categories from a JSON file."
)
parser.add_argument(
    "--input",
    "-i",
    type=str,
    required=True,
    help="Input JSON file with license categories",
)
parser.add_argument(
    "--config",
    "-c",
    type=str,
    default="config.json",
    help="Path to the configuration JSON file",
)


def run_register_license_categories() -> None:
    """Run the register_license_categories script."""
    args = parser.parse_args()
    logger = CustomLogger(name=__name__, stream_level="info")
    config = AppConfig.from_jsonfile(args.config)
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file does not exist: {args.input}")
        return

    with open(input_path, "r", encoding="utf-8") as fin:
        data = json.load(fin)
        categories = data.get("categories", [])
        license_categories = [
            LicenseCategory.model_validate(cat) for cat in categories
        ]

    db_manager = DatabaseManager(engine_url=config.db_engine_url)
    session = db_manager.get_session_instance()
    repo = db_manager.license_category(session)
    for category in license_categories:
        license_category = LicenseCategory(name=category.name)
        repo.create(license_category)
        logger.info(f"Registered category: {category.name}")
