"""Software repo."""

from sqlmodel import Session
from sqlmodel import select

from lynkscan.db.models import Software
from lynkscan.db.models import SoftwareUpdate


class SoftwareRepository:
    """Repository to edit Software table."""

    def __init__(self, session: Session):
        """Initialize SoftwareRepository instance."""
        self.session = session

    def create(self, software: Software) -> Software:
        """Create new software."""
        self.session.add(software)
        self.session.commit()
        self.session.refresh(software)
        return software

    def read(self, id: int) -> Software | None:
        """Read software data."""
        statement = select(Software).where(Software.id == id)
        software = self.session.exec(statement).first()
        return software

    def read_by_identifier_and_category(
        self, identifier: str, category_id: int
    ) -> Software | None:
        """Read software data by identifier and category_id."""
        statement = select(Software).where(
            (Software.identifier == identifier)
            & (Software.category_id == category_id)
        )
        software = self.session.exec(statement).first()
        return software

    def update(self, id: int, new_software: SoftwareUpdate) -> Software | None:
        """Update existing software data."""
        try:
            statement = select(Software).where(Software.id == id)
            software = self.session.exec(statement).first()
            if software is not None:
                software_data = new_software.model_dump(
                    exclude_unset=True, exclude_none=True
                )
                software.sqlmodel_update(software_data)
                self.session.add(software)
                self.session.commit()
                self.session.refresh(software)
                return software
        except Exception:
            return None

    def delete(self, id: int) -> str:
        """Delete a software."""
        try:
            statement = select(Software).where(Software.id == id)
            software = self.session.exec(statement).first()
            if software is not None:
                self.session.delete(software)
                self.session.commit()
                return f"Successed to delete software {id}"
            else:
                return f"Software {id} is not found."
        except Exception:
            return f"Failed to delete a software {id}."
