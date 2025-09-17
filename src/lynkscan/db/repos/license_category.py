"""Repository for LicenseCategory model."""

from typing import Iterable

from sqlmodel import Session
from sqlmodel import select

from lynkscan.db.models import LicenseCategory


class LicenseCategoryRepository:
    """CRUD operations for LicenseCategory table."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with an active session."""
        self.session = session

    def get(self, id: int) -> LicenseCategory | None:
        """Retrieve a license category by id."""
        statement = select(LicenseCategory).where(LicenseCategory.id == id)
        return self.session.exec(statement).first()

    def list(self) -> Iterable[LicenseCategory]:
        """List all license categories."""
        statement = select(LicenseCategory)
        return self.session.exec(statement)

    def create(self, category: LicenseCategory) -> LicenseCategory:
        """Create a new license category record."""
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def update(self, category: LicenseCategory) -> LicenseCategory:
        """Persist updates to an existing license category."""
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete(self, category: LicenseCategory) -> None:
        """Delete a license category record."""
        self.session.delete(category)
        self.session.commit()
