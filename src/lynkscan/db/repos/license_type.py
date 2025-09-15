"""LicenseType repository."""

from sqlmodel import Session
from sqlmodel import select

from lynkscan.db.models import LicenseType
from lynkscan.db.models import LicenseTypeUpdate


class LicenseTypeRepository:
    """Repository to edit LicenseType table."""

    def __init__(self, session: Session):
        """Initialize repository with a SQLModel session."""
        self.session = session

    def create(self, item: LicenseType) -> LicenseType:
        """Create a new LicenseType record."""
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def read(self, id: int) -> LicenseType | None:
        """Read a LicenseType by id."""
        statement = select(LicenseType).where(LicenseType.id == id)
        return self.session.exec(statement).first()

    def update(
        self, id: int, new_item: LicenseTypeUpdate
    ) -> LicenseType | None:
        """Update fields of a LicenseType by id."""
        try:
            statement = select(LicenseType).where(LicenseType.id == id)
            item = self.session.exec(statement).first()
            if item is not None:
                data = new_item.model_dump(
                    exclude_unset=True, exclude_none=True
                )
                item.sqlmodel_update(data)
                self.session.add(item)
                self.session.commit()
                self.session.refresh(item)
                return item
        except Exception:
            return None

    def delete(self, id: int) -> str:
        """Delete a LicenseType by id and return a status message."""
        try:
            statement = select(LicenseType).where(LicenseType.id == id)
            item = self.session.exec(statement).first()
            if item is not None:
                self.session.delete(item)
                self.session.commit()
                return f"Successed to delete license_type {id}"
            else:
                return f"LicenseType {id} is not found."
        except Exception:
            return f"Failed to delete a license_type {id}."
