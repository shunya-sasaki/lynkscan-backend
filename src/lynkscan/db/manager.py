"""DatabaseManager class to operate on the database."""

from typing import Generator

from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import text

from lynkscan.db.repos import SoftwareRepository


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

    def software(self, session: Session) -> SoftwareRepository:
        """Get the SoftwareRepository instance."""
        return SoftwareRepository(session)
