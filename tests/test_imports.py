"""
Test DazzleNodes imports and basic functionality.

Note: These tests validate the aggregator code only.
Individual nodes test themselves in their own repositories.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


def test_version_import():
    """Test that version module can be imported."""
    import version
    assert hasattr(version, "__version__")
    assert hasattr(version, "VERSION")
    assert hasattr(version, "BASE_VERSION")
    assert hasattr(version, "PIP_VERSION")


def test_version_from_import():
    """Test specific version imports."""
    from version import __version__, VERSION, BASE_VERSION, PIP_VERSION
    assert __version__ is not None
    assert VERSION is not None
    assert BASE_VERSION is not None
    assert PIP_VERSION is not None


def test_init_file_exists():
    """Test __init__.py exists and can be read."""
    root = Path(__file__).parent.parent
    init_file = root / "__init__.py"

    assert init_file.exists(), "__init__.py missing"

    # Read content with UTF-8 encoding
    content = init_file.read_text(encoding='utf-8')

    # Should import version
    assert "from .version import" in content or "import version" in content, \
        "__init__.py doesn't import version"

    # Should define NODE_CLASS_MAPPINGS
    assert "NODE_CLASS_MAPPINGS" in content, \
        "__init__.py doesn't define NODE_CLASS_MAPPINGS"

    # Should define WEB_DIRECTORY
    assert "WEB_DIRECTORY" in content, \
        "__init__.py doesn't define WEB_DIRECTORY"


def test_init_exports():
    """Test __init__.py exports expected symbols."""
    root = Path(__file__).parent.parent
    init_file = root / "__init__.py"

    content = init_file.read_text(encoding='utf-8')

    # Check __all__ definition
    assert "__all__" in content, "__init__.py doesn't define __all__"

    # Should export version symbols
    assert "'__version__'" in content or '"__version__"' in content, \
        "__init__.py doesn't export __version__"


def test_sync_script_exists():
    """Test sync_web_files.py exists and has main function."""
    root = Path(__file__).parent.parent
    sync_script = root / "scripts" / "sync_web_files.py"

    assert sync_script.exists(), "sync_web_files.py missing"

    content = sync_script.read_text()

    # Should have sync_web_files function
    assert "def sync_web_files" in content, \
        "sync_web_files.py missing sync_web_files function"

    # Should have main function
    assert "def main" in content, \
        "sync_web_files.py missing main function"


def test_pyproject_imports():
    """Test pyproject.toml can be parsed."""
    root = Path(__file__).parent.parent
    pyproject_path = root / "pyproject.toml"

    assert pyproject_path.exists()

    # Try to parse as TOML (if tomli/tomllib available)
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # Fallback for older Python
        except ImportError:
            pytest.skip("TOML library not available")

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    assert "project" in data, "pyproject.toml missing [project] section"
    assert "name" in data["project"], "pyproject.toml missing project.name"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
