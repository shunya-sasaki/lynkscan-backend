"""License repository."""

from sqlmodel import Session
from sqlmodel import select

from lynkscan.db.models import License
from lynkscan.db.models import LicenseUpdate


class LicenseRepository:
    """Repository to edit License table."""

    def __init__(self, session: Session):
        """Initialize repository with a SQLModel session."""
        self.session = session

    def create(self, item: License) -> License:
        """Create a new License record."""
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def read(self, id: int) -> License | None:
        """Read a License by id."""
        statement = select(License).where(License.id == id)
        return self.session.exec(statement).first()

    def read_by_identifier(self, identifier: str) -> License | None:
        """Read a License by SPDX identifier."""
        statement = select(License).where(License.identifier == identifier)
        return self.session.exec(statement).first()

    def update(self, id: int, new_item: LicenseUpdate) -> License | None:
        """Update fields of a License by id."""
        try:
            statement = select(License).where(License.id == id)
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
        """Delete a License by id and return a status message."""
        try:
            statement = select(License).where(License.id == id)
            item = self.session.exec(statement).first()
            if item is not None:
                self.session.delete(item)
                self.session.commit()
                return f"Successed to delete license {id}"
            else:
                return f"License {id} is not found."
        except Exception:
            return f"Failed to delete a license {id}."
