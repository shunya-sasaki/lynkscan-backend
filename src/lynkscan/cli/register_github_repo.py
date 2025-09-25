"""Fetch GitHub repo informations."""

# %%
import datetime
from argparse import ArgumentParser

from lynkscan.db.manager import DatabaseManager
from lynkscan.db.models import Software
from lynkscan.db.models import SoftwareGitHubEvaluation
from lynkscan.db.models import SoftwareGitHubEvaluationUpdate
from lynkscan.db.models import SoftwareUpdate
from lynkscan.db.models import SoftwareVulnerability
from lynkscan.db.models import SoftwareVulnerabilityUpdate
from lynkscan.db.models import Vulnerability
from lynkscan.llm.license_detector import LicenseDetector
from lynkscan.models import AppConfig
from lynkscan.scanners.github import GitHubRepo
from lynkscan.utils import CustomLogger

logger = CustomLogger(name="fetch-github")

parser = ArgumentParser(
    description="Register license categories from a JSON file."
)
parser.add_argument(
    "--config",
    "-c",
    type=str,
    default="config.json",
    help="Path to the configuration JSON file",
)
parser.add_argument(
    "--owner",
    "-o",
    type=str,
    required=True,
    help="GitHub repository owner",
)
parser.add_argument(
    "--repo",
    "-r",
    type=str,
    required=True,
    help="GitHub repository name",
)


def register_software(db_manager: DatabaseManager, repo: GitHubRepo):
    """Register or update software information in the database."""
    session = db_manager.get_session_instance()
    license_repo = db_manager.license(session)
    license = license_repo.read_by_identifier(repo.license)
    software_category_repo = db_manager.software_category(session)
    software_category_obj = software_category_repo.read_by_name(
        "GitHub Repository"
    )
    software_repo = db_manager.software(session)
    existing_software = software_repo.read_by_identifier_and_category(
        repo.identifier, software_category_obj.id
    )
    if existing_software is None:
        software = software_repo.create(
            Software(
                name=repo.repo,
                identifier=f"{repo.owner}/{repo.repo}",
                latest_version=repo.latest_version,
                official_site_url=repo.homepage,
                repo_url=f"{repo.repo_url}",
                category_id=software_category_obj.id,
                license_id=license.id,
            )
        )
        logger.info(f"Created software with ID: {software.id}")
    else:
        logger.info(f"Software already exists with ID: {existing_software.id}")
        software = software_repo.update(
            existing_software.id,
            SoftwareUpdate(
                name=repo.repo,
                identifier=repo.identifier,
                latest_version=repo.latest_version,
                official_site_url=repo.homepage,
                repo_url=repo.repo_url,
                license_id=license.id,
                category_id=software_category_obj.id,
            ),
        )


def register_github_evaluation(db_manager: DatabaseManager, repo: GitHubRepo):
    """Register or update GitHub evaluation metrics for a software."""
    session = db_manager.get_session_instance()
    software_category_repo = db_manager.software_category(session)
    software_category_obj = software_category_repo.read_by_name(
        "GitHub Repository"
    )
    software_repo = db_manager.software(session)
    existing_software = software_repo.read_by_identifier_and_category(
        repo.identifier, software_category_obj.id
    )
    software_github_eval_repo = db_manager.software_github_evaluation(session)
    existing_eval = software_github_eval_repo.read_by_software_id(
        existing_software.id
    )
    if existing_eval is None:
        software_github_evaluation = software_github_eval_repo.create(
            SoftwareGitHubEvaluation(
                software_id=existing_software.id,
                stars=repo.stars,
                has_sponsors=repo.has_sponsors,
                is_authorized_developer=repo.is_verified,
                last_checked_time=datetime.datetime.now(),
            )
        )
        logger.info(f"Created with ID: {software_github_evaluation.id}")
    else:
        logger.info(f"Target already exists with ID: {existing_eval.id}")
        software_github_evaluation = software_github_eval_repo.update(
            existing_eval.id,
            SoftwareGitHubEvaluationUpdate(
                software_id=existing_software.id,
                stars=repo.stars,
                has_sponsors=repo.has_sponsors,
                is_authorized_developer=repo.is_verified,
                last_checked_time=datetime.datetime.now(),
            ),
        )


def register_vulnerabilities(
    db_manager: DatabaseManager, repo: GitHubRepo, exclude_tags=["stable"]
):
    """Register vulnerabilities associated with the software releases."""
    session = db_manager.get_session_instance()
    vuln_repo = db_manager.vulnerability(session)
    soft_vuln_repo = db_manager.software_vulnerability(session)
    for release in repo.previous_releases:
        if release.tag in exclude_tags:
            continue
        logger.info(f"Release: {release.tag}")
        for vuln in release.vulnerabilities:
            if vuln.cve_id is not None:
                existing_vuln = vuln_repo.read_by_cve_id(vuln.cve_id)
            elif vuln.ghsa_id is not None:
                existing_vuln = vuln_repo.read_by_ghsa_id(vuln.ghsa_id)
            else:
                raise ValueError(
                    "Vulnerability must have either cve_id or ghsa_id"
                )
            if existing_vuln is None:
                vulnerability = vuln_repo.create(
                    Vulnerability(
                        cve_id=vuln.cve_id,
                        ghsa_id=vuln.ghsa_id,
                        cvss=vuln.cvss_score,
                    )
                )
                vuln_id = vulnerability.id
            else:
                vuln_id = existing_vuln.id

            software_category_repo = db_manager.software_category(session)
            software_category_obj = software_category_repo.read_by_name(
                "GitHub Repository"
            )
            software_repo = db_manager.software(session)
            existing_software = software_repo.read_by_identifier_and_category(
                repo.identifier, software_category_obj.id
            )
            if existing_software is None:
                raise ValueError("Software must be registered first")

            logger.info(
                f"vuln_id: {vuln_id}, existing_software.id: {existing_software.id}, release.tag: {release.tag}"
            )
            existing_soft_vuln = soft_vuln_repo.read_by_attrs(
                existing_software.id, release.tag, vuln_id
            )
            if existing_soft_vuln is None:
                soft_vuln = soft_vuln_repo.create(
                    SoftwareVulnerability(
                        software_id=existing_software.id,
                        software_version=release.tag,
                        vuln_id=vuln_id,
                    )
                )
                logger.info(
                    f"Created SoftwareVulnerability with ID: {soft_vuln.id}"
                )
            else:
                logger.info(
                    f"SoftwareVulnerability already exists with ID: {existing_soft_vuln.id}"
                )
                soft_vuln = soft_vuln_repo.update(
                    existing_soft_vuln.id,
                    SoftwareVulnerabilityUpdate(
                        software_id=existing_software.id,
                        software_version=release.tag,
                        vuln_id=vuln_id,
                    ),
                )


def run():
    """Main function to execute the script."""
    args = parser.parse_args()
    config = AppConfig.from_jsonfile(args.config)
    db_manager = DatabaseManager(config.db_engine_url)
    repo = GitHubRepo(
        owner=args.owner, repo=args.repo, verify=config.network.verify_ssl
    )
    repo.fetch_infos(with_file=True)
    if repo.license == "NOASSERTION":
        license_text = repo.fetch_license_text()
        detector = LicenseDetector(model=config.llm.detector_model)
        license = detector.run(license_text)
        repo.license = license.identifier
    register_software(db_manager, repo)
    register_github_evaluation(db_manager, repo)
    register_vulnerabilities(db_manager, repo, exclude_tags=["stable"])
