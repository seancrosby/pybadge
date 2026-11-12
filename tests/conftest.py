"""Shared fixtures for the headless eBadge API tests."""

import pytest

from testing import session


@pytest.fixture
def badge_backend():
    """Run a test with an initialized headless eBadge backend."""
    with session() as backend:
        yield backend
