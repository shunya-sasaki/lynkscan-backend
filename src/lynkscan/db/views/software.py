"""Views for the database."""
# views/software.py

from __future__ import annotations

from sqlalchemy import func  # ← 追加
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

    @staticmethod
    def selectable():
        stmt = (
            select(
                Software.id.label("software_id"),
                SoftwareVulnerability.software_version.label(
                    "software_version"
                ),
                Vulnerability.cve_id.label("vuln_cve"),
                Vulnerability.cvss.label("vuln_cvss"),
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
        stmt = (
            select(
                Software.id.label("software_id"),
                SoftwareVulnerability.software_version.label(
                    "software_version"
                ),
                Vulnerability.cve_id.label("vuln_cve"),
                Vulnerability.cvss.label("vuln_cvss"),
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
    max_cvss: float | None
    official_site_url: str
    repo_url: str

    @staticmethod
    def get_views(session: Session) -> list[SoftwareView]:
        vuln_sq = SoftwareVulnView.selectable()

        stmt = (
            select(
                Software.name.label("name"),
                SoftwareCategory.name.label("category"),
                Software.identifier.label("identifier"),
                Software.latest_version.label("latest_version"),
                License.name.label("license"),
                Software.official_site_url.label("official_site_url"),
                Software.repo_url.label("repo_url"),
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
                isouter=True,  # ← 脆弱性が無いソフトも含める
            )
            # 非集計列をGROUP BY
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
