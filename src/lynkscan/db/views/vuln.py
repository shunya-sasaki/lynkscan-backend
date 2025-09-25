"""Views for the database."""
# views/software.py

from __future__ import annotations

from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import select

from lynkscan.db.models import Software
from lynkscan.db.models import SoftwareCategory
from lynkscan.db.models import SoftwareVulnerability
from lynkscan.db.models import Vulnerability


class VulnView(SQLModel, table=False):
    """View to join Software with SoftwareVulnerability and Vulnerability."""

    software_name: str
    software_category: str
    software_identifier: str
    software_version: str
    cve: str | None
    ghsa: str | None
    cvss: float | None
    severity: str | None

    def get_views(session: Session) -> list[VulnView]:
        stmt = (
            select(
                Software.name.label("software_name"),
                SoftwareCategory.name.label("software_category"),
                Software.identifier.label("software_identifier"),
                SoftwareVulnerability.software_version.label(
                    "software_version"
                ),
                Vulnerability.cve_id.label("cve"),
                Vulnerability.ghsa_id.label("ghsa"),
                Vulnerability.cvss.label("cvss"),
                Vulnerability.severity.label("severity"),
            )
            .join(
                SoftwareCategory,
                Software.category_id == SoftwareCategory.id,
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
        results = session.exec(stmt).all()
        return [VulnView.model_validate(row) for row in results]
