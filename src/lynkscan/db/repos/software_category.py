"""SoftwareCategory repository."""

from sqlmodel import Session
from sqlmodel import select

from lynkscan.db.models import SoftwareCategory
from lynkscan.db.models import SoftwareCategoryUpdate


class SoftwareCategoryRepository:
    """Repository to edit SoftwareCategory table."""

    def __init__(self, session: Session):
        """Initialize repository with a SQLModel session."""
        self.session = session

    def create(self, item: SoftwareCategory) -> SoftwareCategory:
        """Create a new SoftwareCategory record."""
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def read(self, id: int) -> SoftwareCategory | None:
        """Read a SoftwareCategory by id."""
        statement = select(SoftwareCategory).where(
            SoftwareCategory.id == id
        )
        return self.session.exec(statement).first()

    def update(
        self, id: int, new_item: SoftwareCategoryUpdate
    ) -> SoftwareCategory | None:
        """Update fields of a SoftwareCategory by id."""
        try:
            statement = select(SoftwareCategory).where(
                SoftwareCategory.id == id
            )
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
        """Delete a SoftwareCategory by id and return a status message."""
        try:
            statement = select(SoftwareCategory).where(
                SoftwareCategory.id == id
            )
            item = self.session.exec(statement).first()
            if item is not None:
                self.session.delete(item)
                self.session.commit()
                return f"Successed to delete software_category {id}"
            else:
                return f"SoftwareCategory {id} is not found."
        except Exception:
            return f"Failed to delete a software_category {id}."
