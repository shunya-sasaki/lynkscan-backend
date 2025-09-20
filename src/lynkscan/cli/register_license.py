"""Register a license info with LynkScan.

Before running this command, ensure that the license categories are
registered using the `register_license_categories` command.
"""

import json
from argparse import ArgumentParser
from pathlib import Path

from lynkscan.db.manager import DatabaseManager
from lynkscan.db.models import License
from lynkscan.models import AppConfig
from lynkscan.models import LicenseInfo
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


def run_register_license() -> None:
    """Run the register_license script."""
    args = parser.parse_args()
    logger = CustomLogger(name=__name__, stream_level="info")
    config = AppConfig.from_jsonfile(args.config)
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file does not exist: {args.input}")
        return

    with open(input_path, "r", encoding="utf-8") as fin:
        data = json.load(fin)
        licenses = data.get("licenses", [])
        license_objs = [LicenseInfo.model_validate(lic) for lic in licenses]

    db_manager = DatabaseManager(engine_url=config.db_engine_url)
    session = db_manager.get_session_instance()
    license_repo = db_manager.license(session)
    category_repo = db_manager.license_category(session)

    for lic in license_objs:
        category = category_repo.read_by_name(lic.category)
        if not category:
            logger.error(
                f"Category '{lic.category}' does not exist. "
                "Please register it first."
            )
            continue
        license_entry = License(
            name=lic.full_name,
            identifier=lic.identifier,
            is_fsf_free=lic.is_fsf_free,
            is_osi_approved=lic.is_osi_approved,
            category_id=category.id,
        )
        license_repo.create(license_entry)
        logger.info(f"Registered license: {lic.full_name}")
