# DazzleNodes Tests

Tests for DazzleNodes aggregator code.

## Philosophy

**Individual nodes test themselves** - Each node in `nodes/` has its own test suite in its repository.

**DazzleNodes tests focus on aggregation** - These tests validate:
- Version tracking system
- Import structure and exports
- Auto-sync functionality
- Project structure integrity
- Integration of submodules

## Running Tests

### Local Testing (Recommended)

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_version.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run fast (no coverage)
pytest tests/ -x  # Stop on first failure
```

### CI/CD Testing

Tests automatically run on GitHub Actions for:
- Push to main, dev branches
- Pull requests to main, dev

See `.github/workflows/main.yml` for configuration.

## Test Files

### `test_version.py`
Tests for version.py module:
- Version imports work
- Version format is correct (VERSION_BRANCH_BUILD-YYYYMMDD-HASH)
- BASE_VERSION is semantic (0.1.0-alpha)
- PIP_VERSION is PEP 440 compliant
- Helper functions work correctly

### `test_structure.py`
Tests for project structure:
- Required files exist (__init__.py, version.py, pyproject.toml, etc.)
- Versioning scripts exist (update-version.sh, install-hooks.sh)
- Git hooks exist (pre-commit, post-commit, pre-push)
- GitHub workflows exist (publish-to-registry.yml)
- Directory structure is correct

### `test_imports.py`
Tests for import functionality:
- version module imports correctly
- __init__.py structure is correct
- Exports are defined (__all__)
- sync_web_files.py exists and has main function
- pyproject.toml can be parsed

## Test Coverage Goals

- **Version tracking**: 100% (critical for releases)
- **Imports**: 100% (critical for ComfyUI loading)
- **Structure**: 90%+ (catches missing files early)

## Adding New Tests

When adding new aggregator functionality:
1. Add tests to appropriate test file
2. Run locally with `pytest tests/ -v`
3. Ensure coverage stays high
4. Update this README if adding new test file

**Note**: Don't test individual node functionality here. Those tests belong in the node's own repository.

## Troubleshooting

### ImportError: No module named 'version'

**Cause**: Python path not set correctly

**Fix**: Run from project root or use conftest.py:
```bash
cd /c/code/DazzleNodes/github
pytest tests/
```

### Tests pass locally but fail in CI

**Cause**: Missing dependencies in CI environment

**Fix**: Update `pyproject.toml` [project.optional-dependencies] dev section

### Submodule tests failing

**Cause**: Submodules not initialized

**Fix**: Tests should NOT depend on submodules being present. Aggregator tests only.
