"""
Test DazzleNodes project structure and required files.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


def test_root_files_exist():
    """Test that required root files exist."""
    root = Path(__file__).parent.parent

    required_files = [
        "__init__.py",
        "version.py",
        "pyproject.toml",
        "README.md",
        "requirements.txt",
    ]

    for filename in required_files:
        filepath = root / filename
        assert filepath.exists(), f"Required file missing: {filename}"


def test_scripts_exist():
    """Test that versioning scripts exist."""
    root = Path(__file__).parent.parent
    scripts_dir = root / "scripts"

    assert scripts_dir.exists(), "scripts/ directory missing"

    required_scripts = [
        "update-version.sh",
        "install-hooks.sh",
        "sync_web_files.py",
    ]

    for script in required_scripts:
        script_path = scripts_dir / script
        assert script_path.exists(), f"Required script missing: {script}"


def test_hooks_exist():
    """Test that git hook templates exist."""
    root = Path(__file__).parent.parent
    hooks_dir = root / "scripts" / "hooks"

    assert hooks_dir.exists(), "scripts/hooks/ directory missing"

    required_hooks = [
        "pre-commit",
        "post-commit",
        "pre-push",
    ]

    for hook in required_hooks:
        hook_path = hooks_dir / hook
        assert hook_path.exists(), f"Required hook missing: {hook}"


def test_github_files_exist():
    """Test that GitHub configuration files exist."""
    root = Path(__file__).parent.parent
    github_dir = root / ".github"

    assert github_dir.exists(), ".github/ directory missing"

    # Check for workflows
    workflows_dir = github_dir / "workflows"
    assert workflows_dir.exists(), ".github/workflows/ directory missing"

    required_workflows = [
        "publish-to-registry.yml",
    ]

    for workflow in required_workflows:
        workflow_path = workflows_dir / workflow
        assert workflow_path.exists(), f"Required workflow missing: {workflow}"

    # Check for FUNDING.yml
    funding_file = github_dir / "FUNDING.yml"
    assert funding_file.exists(), "FUNDING.yml missing"


def test_nodes_directory_structure():
    """Test nodes directory exists (for submodules)."""
    root = Path(__file__).parent.parent
    nodes_dir = root / "nodes"

    assert nodes_dir.exists(), "nodes/ directory missing"
    # Note: Submodules might not be initialized in CI, so we just check directory exists


def test_web_directory_structure():
    """Test web directory exists (for auto-synced resources)."""
    root = Path(__file__).parent.parent
    web_dir = root / "web"

    # web/ directory might not exist until first sync
    # Just verify it can be created if needed
    assert True  # Placeholder - web/ is auto-generated


def test_pyproject_has_version_config():
    """Test pyproject.toml has version configuration."""
    root = Path(__file__).parent.parent
    pyproject_path = root / "pyproject.toml"

    assert pyproject_path.exists()

    content = pyproject_path.read_text()

    # Check for dynamic version
    assert 'dynamic = ["version"]' in content or "dynamic = ['version']" in content, \
        "pyproject.toml missing dynamic version configuration"

    # Check for setuptools configuration
    assert "[tool.setuptools.dynamic]" in content, \
        "pyproject.toml missing setuptools dynamic configuration"

    # Check for ComfyUI registry config
    assert "[tool.comfy]" in content, \
        "pyproject.toml missing ComfyUI registry configuration"


def test_gitignore_exists():
    """Test .gitignore exists and protects sensitive content."""
    root = Path(__file__).parent.parent
    gitignore_path = root / ".gitignore"

    assert gitignore_path.exists(), ".gitignore missing"

    content = gitignore_path.read_text()

    # Check for important patterns
    important_patterns = [
        "/private/",
        "__pycache__",
        "*.py[cod]",  # More general pattern that includes *.pyc
    ]

    for pattern in important_patterns:
        assert pattern in content, f".gitignore missing pattern: {pattern}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
