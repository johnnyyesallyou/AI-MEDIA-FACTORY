"""
Sprint 66.4: Pytest Configuration for Async Tests

Configures pytest-asyncio and test fixtures for both unit and integration tests.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Set test mode BEFORE importing FastAPI/main
os.environ["APP_ENV"] = "test"

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Pytest-asyncio configuration
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_configure(config):
    """Register custom markers and configure asyncio mode."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async (requires pytest-asyncio)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration (requires external services)"
    )
