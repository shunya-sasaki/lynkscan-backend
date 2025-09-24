"""SoftwareGitHubEvaluation table models."""

from datetime import datetime

from sqlmodel import Field
from sqlmodel import SQLModel


class SoftwareGitHubEvaluationBase(SQLModel):
    """Base fields for SoftwareGitHubEvalation."""

    software_id: int = Field(foreign_key="software.id")
    stars: int = 0
    has_sponsors: bool = False
    is_authorized_developer: bool = False
    last_checked_time: datetime | None = None


class SoftwareGitHubEvaluation(SoftwareGitHubEvaluationBase, table=True):
    """GitHub repository evaluation metrics for a Software identifier."""

    __tablename__ = "software_github_evaluation"

    id: int | None = Field(default=None, primary_key=True)


class SoftwareGitHubEvaluationUpdate(SQLModel):
    """Partial update for SoftwareGitHubEvaluation."""

    software_id: int = Field(foreign_key="software.id")
    stars: int | None = None
    has_sponsors: bool | None = None
    is_authorized_developer: bool | None = None
    last_checked_time: datetime | None = None
