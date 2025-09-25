"""Views for the database."""

from __future__ import annotations

from sqlalchemy import case
from sqlalchemy import func
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import select

from lynkscan.db.models import License
from lynkscan.db.models import Software
from lynkscan.db.models import SoftwareCategory
from lynkscan.db.models import SoftwareVulnerability
from lynkscan.db.models import Vulnerability


class SoftwareVulnView(SQLModel, table=False):
    """View to join Software with SoftwareVulnerability and Vulnerability."""

    software_id: int
    software_version: str
    vuln_cve: str | None
    vuln_cvss: float | None
    vuln_severity: str | None

    @staticmethod
    def selectable():
        """Return a selectable subquery joining software and vulnerabilities.

        Joins Software -> SoftwareVulnerability -> Vulnerability and exposes
        software_id, software_version, vuln_cve, vuln_cvss, vuln_severity.
        """
        stmt = (
            select(
                Software.id.label("software_id"),
                SoftwareVulnerability.software_version.label(
                    "software_version"
                ),
                Vulnerability.cve_id.label("vuln_cve"),
                Vulnerability.cvss.label("vuln_cvss"),
                Vulnerability.severity.label("vuln_severity"),
            )
            .join(
                SoftwareVulnerability,
                Software.id == SoftwareVulnerability.software_id,
            )
            .join(
                Vulnerability,
                SoftwareVulnerability.vuln_id == Vulnerability.id,
            )
        )
        return stmt.subquery("software_vuln_view")

    @staticmethod
    def get_views(session: Session) -> list[SoftwareVulnView]:
        """Query and materialize SoftwareVulnView rows.

        Parameters:
        session : Session
            Active SQLModel/SQLAlchemy session.

        Returns:
        list[SoftwareVulnView]
            Result rows validated into the view model.
        """
        stmt = (
            select(
                Software.id.label("software_id"),
                SoftwareVulnerability.software_version.label(
                    "software_version"
                ),
                Vulnerability.cve_id.label("vuln_cve"),
                Vulnerability.cvss.label("vuln_cvss"),
                Vulnerability.severity.label("vuln_severity"),
            )
            .join(
                SoftwareVulnerability,
                Software.id == SoftwareVulnerability.software_id,
            )
            .join(
                Vulnerability,
                SoftwareVulnerability.vuln_id == Vulnerability.id,
            )
        )
        rows = session.exec(stmt).all()
        return [SoftwareVulnView.model_validate(r) for r in rows]


class SoftwareView(SQLModel, table=False):
    """View to join Software with SoftwareCategory and License."""

    name: str
    category: str
    identifier: str
    latest_version: str | None
    license: str | None
    severity: str | None
    max_cvss: float | None
    official_site_url: str
    repo_url: str

    @staticmethod
    def get_views(session: Session) -> list[SoftwareView]:
        """Return the software view rows with severity for latest versions.

        The severity is the highest severity among vulnerabilities that affect
        the software's latest_version. If there are no vulnerabilities, the
        severity is "none". Also returns the max CVSS for the latest version.
        """
        vuln_sq = SoftwareVulnView.selectable()

        severity_rank = func.max(
            case(
                (vuln_sq.c.vuln_severity == "critical", 5),
                (vuln_sq.c.vuln_severity == "high", 4),
                (vuln_sq.c.vuln_severity == "medium", 3),
                (vuln_sq.c.vuln_severity == "low", 2),
                else_=0,
            )
        )

        severity_expr = case(
            (severity_rank == 5, "critical"),
            (severity_rank == 4, "high"),
            (severity_rank == 3, "medium"),
            (severity_rank == 2, "low"),
            else_="none",
        ).label("severity")

        stmt = (
            select(
                Software.name.label("name"),
                SoftwareCategory.name.label("category"),
                Software.identifier.label("identifier"),
                Software.latest_version.label("latest_version"),
                License.name.label("license"),
                Software.official_site_url.label("official_site_url"),
                Software.repo_url.label("repo_url"),
                severity_expr,
                func.max(vuln_sq.c.vuln_cvss).label("max_cvss"),  # ← 集計
            )
            .join(
                SoftwareCategory, Software.category_id == SoftwareCategory.id
            )
            .join(License, Software.license_id == License.id)
            .join(
                vuln_sq,
                (Software.id == vuln_sq.c.software_id)
                & (vuln_sq.c.software_version == Software.latest_version),
                isouter=True,
            )
            .group_by(
                Software.name,
                SoftwareCategory.name,
                Software.identifier,
                Software.latest_version,
                License.name,
                Software.official_site_url,
                Software.repo_url,
            )
        )
        rows = session.exec(stmt).all()
        return [SoftwareView.model_validate(r) for r in rows]
