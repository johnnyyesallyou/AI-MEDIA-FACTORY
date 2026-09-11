"""Global pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models.base import Base


@pytest.fixture(scope="function")
def db_session():
    """
    Create an isolated in-memory SQLite database for each test.
    
    This avoids:
    - UniqueViolation errors (table not cleaned between tests)
    - CircularDependencyError (assets/content FK cycle in postgres)
    - Test isolation issues
    """
    # Create isolated in-memory SQLite engine
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)