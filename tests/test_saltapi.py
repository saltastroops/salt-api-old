"""Unit tests."""

from saltapi import __version__


def test_version():
    """Check for correct version."""
    assert __version__ == '0.1.0'
