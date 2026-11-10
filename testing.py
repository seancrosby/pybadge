"""Helpers for testing programs that use :mod:`pybadge` without hardware."""

from contextlib import contextmanager

from backends.test_backend import TestBackend


def make_backend():
    """Create a deterministic in-memory backend for a test."""
    return TestBackend()


@contextmanager
def session(backend=None):
    """Initialize test mode and always shut it down when the block exits.

    Example::

        with pybadge.testing.session() as board:
            board.press_button(pybadge.BUTTON_A)
            assert pybadge.is_pressed(pybadge.BUTTON_A)
    """
    import pybadge

    backend = backend or make_backend()
    pybadge.initialize(mode="test", backend=backend)
    try:
        yield backend
    finally:
        pybadge.shutdown()
