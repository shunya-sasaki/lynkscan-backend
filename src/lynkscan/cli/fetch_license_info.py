"""Fetch license information from SPDX and categorize them using LLM."""

import datetime
import json
from argparse import ArgumentParser
from io import BytesIO

import pandas as pd
import requests
from bs4 import BeautifulSoup

from lynkscan.llm import LicenseEvaluator
from lynkscan.models import LicenseInfo
from lynkscan.utils import CustomLogger

parser = ArgumentParser(description="Fetch license information from SPDX")
parser.add_argument(
    "--model",
    "-m",
    type=str,
    default="gpt-5",
    help="OpenAI model to use for license categorization",
)
parser.add_argument(
    "--output",
    "-o",
    type=str,
    default="license_info.json",
    help="Output JSON file to save license information",
)


def run_fetch_license_info():
    """Run fetch_license_info script."""
    args = parser.parse_args()
    logger = CustomLogger(name="fetch-license", stream_level="INFO")
    url = "https://spdx.org/licenses/"
    response = requests.get(url)
    bytes = BytesIO(response.content)
    dfs = pd.read_html(bytes)
    df_license = dfs[0]
    evaluator = LicenseEvaluator(model=args.model)

    license_infos: list[LicenseInfo] = []
    n_licenses = len(df_license)

    for index, (
        full_name,
        identifier,
        is_fsf_free,
        is_osi_approved,
    ) in df_license.iterrows():
        license_url = f"https://spdx.org/licenses/{identifier}.html"
        response = requests.get(license_url)
        html = response.content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        page = soup.find("div", id="page")
        license_text = page.prettify()
        category = evaluator.run(identifier, license_text)
        license_info = LicenseInfo(
            full_name=full_name,
            identifier=identifier,
            is_fsf_free=is_fsf_free == "Y",
            is_osi_approved=is_osi_approved == "Y",
            category=category,
        )
        license_infos.append(license_info)
        logger.info(f"{index + 1:04d}/{n_licenses}: {license_info}")

    dict_data = {
        "licenses": [
            license_info.model_dump(by_alias=True)
            for license_info in license_infos
        ],
        "last_updated": datetime.datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"),
    }
    with open(args.output, "w", encoding="utf-8") as fout:
        json.dump(dict_data, fout, indent=2)
