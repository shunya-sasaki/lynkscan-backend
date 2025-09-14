"""Usage table models."""

from sqlmodel import Field
from sqlmodel import SQLModel


class Usage(SQLModel, table=True):
    """Usage table (generic usage texts)."""

    id: int | None = Field(default=None, primary_key=True)
    usage: str


class UsageUpdate(SQLModel):
    """Partial update for Usage."""

    usage: str | None = None
