"""SoftwareGitHubEvaluation repository."""

from sqlmodel import Session
from sqlmodel import select

from lynkscan.db.models import SoftwareGitHubEvaluation
from lynkscan.db.models import SoftwareGitHubEvaluationUpdate


class SoftwareGitHubEvaluationRepository:
    """Repository to edit SoftwareGitHubEvaluation table."""

    def __init__(self, session: Session):
        """Initialize repository with a SQLModel session."""
        self.session = session

    def create(
        self, item: SoftwareGitHubEvaluation
    ) -> SoftwareGitHubEvaluation:
        """Create a new SoftwareGitHubEvaluation record."""
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def read(self, id: int) -> SoftwareGitHubEvaluation | None:
        """Read a SoftwareGitHubEvaluation by id."""
        statement = select(SoftwareGitHubEvaluation).where(
            SoftwareGitHubEvaluation.id == id
        )
        return self.session.exec(statement).first()

    def update(
        self, id: int, new_item: SoftwareGitHubEvaluationUpdate
    ) -> SoftwareGitHubEvaluation | None:
        """Update fields of a SoftwareGitHubEvaluation by id."""
        try:
            statement = select(SoftwareGitHubEvaluation).where(
                SoftwareGitHubEvaluation.id == id
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
        """Delete a SoftwareGitHubEvaluation by id and return a message."""
        try:
            statement = select(SoftwareGitHubEvaluation).where(
                SoftwareGitHubEvaluation.id == id
            )
            item = self.session.exec(statement).first()
            if item is not None:
                self.session.delete(item)
                self.session.commit()
                return (
                    f"Successed to delete software_github_evaluation {id}"
                )
            else:
                return f"SoftwareGitHubEvaluation {id} is not found."
        except Exception:
            return f"Failed to delete a software_github_evaluation {id}."
