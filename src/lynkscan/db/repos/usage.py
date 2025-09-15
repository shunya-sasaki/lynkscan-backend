"""Usage repository."""

from sqlmodel import Session
from sqlmodel import select

from lynkscan.db.models import Usage
from lynkscan.db.models import UsageUpdate


class UsageRepository:
    """Repository to edit Usage table."""

    def __init__(self, session: Session):
        """Initialize repository with a SQLModel session."""
        self.session = session

    def create(self, item: Usage) -> Usage:
        """Create a new Usage record."""
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def read(self, id: int) -> Usage | None:
        """Read a Usage by id."""
        statement = select(Usage).where(Usage.id == id)
        return self.session.exec(statement).first()

    def update(self, id: int, new_item: UsageUpdate) -> Usage | None:
        """Update fields of a Usage by id."""
        try:
            statement = select(Usage).where(Usage.id == id)
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
        """Delete a Usage by id and return a status message."""
        try:
            statement = select(Usage).where(Usage.id == id)
            item = self.session.exec(statement).first()
            if item is not None:
                self.session.delete(item)
                self.session.commit()
                return f"Successed to delete usage {id}"
            else:
                return f"Usage {id} is not found."
        except Exception:
            return f"Failed to delete a usage {id}."
