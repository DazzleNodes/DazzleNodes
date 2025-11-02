"""
Test version.py module functionality.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


def test_version_imports():
    """Test that version module imports correctly."""
    from version import __version__, VERSION, BASE_VERSION, PIP_VERSION
    assert __version__ is not None
    assert VERSION is not None
    assert BASE_VERSION is not None
    assert PIP_VERSION is not None


def test_version_format():
    """Test version string follows expected format."""
    from version import __version__

    # Format: VERSION_BRANCH_BUILD-YYYYMMDD-COMMITHASH
    # Example: 0.1.0-alpha_main_19-20251102-7093590
    assert isinstance(__version__, str)
    assert len(__version__) > 0

    # Should contain underscores (separating components)
    assert "_" in __version__

    # Should contain dashes
    assert "-" in __version__


def test_base_version_format():
    """Test base version is semantic version with optional phase."""
    from version import BASE_VERSION

    # Should be semantic version like "0.1.0" or "0.1.0-alpha"
    assert isinstance(BASE_VERSION, str)
    parts = BASE_VERSION.split("-")[0].split(".")
    assert len(parts) == 3  # MAJOR.MINOR.PATCH

    # Each part should be numeric
    for part in parts:
        assert part.isdigit(), f"Version part '{part}' should be numeric"


def test_pip_version_format():
    """Test PIP version is PEP 440 compliant."""
    from version import PIP_VERSION

    assert isinstance(PIP_VERSION, str)
    # Should not contain underscores (not in full format)
    assert "_" not in PIP_VERSION


def test_version_constants():
    """Test version constants are defined."""
    from version import MAJOR, MINOR, PATCH, PHASE

    assert isinstance(MAJOR, int)
    assert isinstance(MINOR, int)
    assert isinstance(PATCH, int)
    # PHASE can be None or string
    assert PHASE is None or isinstance(PHASE, str)


def test_version_functions():
    """Test version helper functions."""
    from version import get_version, get_base_version, get_pip_version, get_version_dict

    # All functions should return strings
    assert isinstance(get_version(), str)
    assert isinstance(get_base_version(), str)
    assert isinstance(get_pip_version(), str)

    # get_version_dict should return dictionary
    version_dict = get_version_dict()
    assert isinstance(version_dict, dict)
    assert "full" in version_dict
    assert "base" in version_dict
    assert "branch" in version_dict
    assert "build" in version_dict


def test_version_consistency():
    """Test version values are consistent across different access methods."""
    from version import __version__, VERSION, get_version

    # VERSION constant should equal __version__
    assert VERSION == __version__

    # get_version() should return __version__
    assert get_version() == __version__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
