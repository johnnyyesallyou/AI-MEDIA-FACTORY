"""Global pytest configuration and fixtures for test isolation."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base


@pytest.fixture(scope="function")
def db_session():
    """
    Create an isolated in-memory SQLite database for each test.
    
    This avoids:
    - UniqueViolation errors (table not cleaned between tests)
    - CircularDependencyError (assets/content FK cycle in postgres)
    - Test isolation issues
    
    Uses sqlite:///:memory: so each test gets a fresh database.
    """
    # Create isolated in-memory SQLite engine
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Create all tables defined in Base
    Base.metadata.create_all(bind=engine)
    
    # Create session factory bound to this engine
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    
    yield session
    
    # Cleanup: close session and drop all tables
    session.close()
    Base.metadata.drop_all(bind=engine)