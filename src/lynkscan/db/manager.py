"""DatabaseManager class to operate on the database."""

from typing import Generator

from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import text

from lynkscan.db.repos import LicenseCategoryRepository
from lynkscan.db.repos import LicenseRepository
from lynkscan.db.repos import SoftwareCategoryRepository
from lynkscan.db.repos import SoftwareGitHubEvaluationRepository
from lynkscan.db.repos import SoftwareRepository
from lynkscan.db.repos import SoftwareVulnerabilityRepository
from lynkscan.db.repos import UsageRepository
from lynkscan.db.repos import VulnerabilityRepository
from lynkscan.db.views import SoftwareView


class DatabaseManager:
    """Class to manage database operations."""

    def __init__(self, engine_url: str = "sqlite:///lynkscan.db"):
        """Initialize the DatabaseManager with a database engine URL."""
        self.engine_url = engine_url
        self.engine = create_engine(engine_url)

    def create_db_and_tables(self):
        """Create the database and tables."""
        SQLModel.metadata.create_all(self.engine)
        if self.engine_url.startswith("sqlite"):
            with self.engine.connect() as conn:
                conn.execute(text("PRAGMA foreign_keys=ON"))
                conn.commit()

    def get_session(self) -> Generator[Session, None, None]:
        """Get a new database session."""
        with Session(self.engine) as session:
            yield session

    def get_session_instance(self) -> Session:
        """Get a new database session instance."""
        return Session(self.engine)

    def software(self, session: Session) -> SoftwareRepository:
        """Get the SoftwareRepository instance."""
        return SoftwareRepository(session)

    def license_category(self, session: Session) -> LicenseCategoryRepository:
        """Get the LicenseCategoryRepository instance."""
        return LicenseCategoryRepository(session)

    def license(self, session: Session) -> LicenseRepository:
        """Get the LicenseRepository instance."""
        return LicenseRepository(session)

    def software_category(
        self, session: Session
    ) -> SoftwareCategoryRepository:
        """Get the SoftwareCategoryRepository instance."""
        return SoftwareCategoryRepository(session)

    def vulnerability(self, session: Session) -> VulnerabilityRepository:
        """Get the VulnerabilityRepository instance."""
        return VulnerabilityRepository(session)

    def software_vulnerability(
        self, session: Session
    ) -> SoftwareVulnerabilityRepository:
        """Get the SoftwareVulnerabilityRepository instance."""
        return SoftwareVulnerabilityRepository(session)

    def software_github_evaluation(
        self, session: Session
    ) -> SoftwareGitHubEvaluationRepository:
        """Get the SoftwareGitHubEvaluationRepository instance."""
        return SoftwareGitHubEvaluationRepository(session)

    def usage(self, session: Session) -> UsageRepository:
        """Get the UsageRepository instance."""
        return UsageRepository(session)

    def software_view(self, session: Session) -> list[SoftwareView]:
        """Get the SoftwareView instance."""
        return SoftwareView.get_views(session)
