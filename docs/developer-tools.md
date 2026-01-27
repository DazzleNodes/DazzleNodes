# Developer Tools

This document describes the scripts in the `scripts/` directory used for DazzleNodes development, maintenance, and release workflows.

## Overview

| Script | Purpose |
|--------|---------|
| `dev_mode.py` | Toggle nodes between dev mode (symlinks) and publish mode (submodules) |
| `sync_web_files.py` | Sync JavaScript/CSS from submodules into the unified `web/` directory |
| `sync-submodules.sh` | Update all submodules to their latest released versions |
| `update-version.sh` | Update `__version__` string in `version.py` with branch/build/date metadata |
| `install-hooks.sh` | Install git hooks for automatic version updates and branch protection |
| `fix_python_association.cmd` | Fix Windows file association when `.py` files open in the wrong Python |

## dev_mode.py — Development Mode Toggle

Manages switching nodes between two modes:

- **Dev mode** (symlinks): Direct links to your local source repositories for rapid iteration — changes are immediately visible in ComfyUI without any commit/pull cycle.
- **Publish mode** (submodules): Standard git submodules for version control and distribution.

### Requirements

```bash
cd scripts
pip install -r requirements.txt  # pyyaml>=6.0
```

Always run with `python dev_mode.py` (not just `dev_mode.py`) to ensure the correct interpreter.

### Commands

```bash
# Check current state of all nodes
python scripts/dev_mode.py status
python scripts/dev_mode.py status --complete   # Detailed with git info

# Switch to dev mode (creates symlinks to local repos)
python scripts/dev_mode.py dev smart-resolution-calc
python scripts/dev_mode.py dev all

# Switch to publish mode (restores submodules)
python scripts/dev_mode.py publish smart-resolution-calc
python scripts/dev_mode.py publish all
```

### Global Options

```bash
-v, --verbose    # Detailed operation logs
--dry-run        # Preview changes without making them
--no-backup      # Skip backup creation (not recommended)
```

### Configuring Local Development Paths

By default, `dev_mode.py` reads source paths from `.gitmodules`. Since those are typically GitHub URLs (not local filesystem paths), the script needs another way to find your local repos.

**Setup:**

```bash
cd scripts
cp dev_mode_local.yaml.example dev_mode_local.yaml
```

Edit `dev_mode_local.yaml` with your local paths:

```yaml
node_paths:
  smart-resolution-calc: "C:\\code\\smart-resolution-calc-repo\\Local"
  fit-mask-to-image: "C:\\code\\ComfyUI-ImageMask-Fix\\local"
  dazzle-comfy-plasma-fast: "C:\\code\\dazzle-comfy-plasma-fast"
  preview-bridge-extended: "C:\\code\\ComfyUI-PreviewBridgeExtended"
```

> **Note:** `dev_mode_local.yaml` is gitignored — it's specific to your machine and never committed.

**Usage with local paths:**

```bash
# Default: uses gitmodules first, falls back to local config if path isn't local
python scripts/dev_mode.py dev smart-resolution-calc

# Prefer local config over gitmodules
python scripts/dev_mode.py dev smart-resolution-calc --local

# Switch all nodes to dev mode using local paths
python scripts/dev_mode.py dev all --local
```

**Path resolution order:**

| Flag | Priority |
|------|----------|
| (default) | `.gitmodules` path → fall back to `dev_mode_local.yaml` if not a local path |
| `--local` | `dev_mode_local.yaml` → fall back to `.gitmodules` |

### Configuration File

Edit `dev_mode_config.yaml` to set defaults:

```yaml
status_default_mode: quick   # or "complete"
backup_enabled: true
verbose: false
```

Environment variables override the config file:
- `DEV_MODE_STATUS_DEFAULT` — `quick` or `complete`
- `DEV_MODE_VERBOSE` — `1`, `true`, or `yes`

### Typical Workflow

```bash
# 1. Switch to dev mode
python scripts/dev_mode.py dev all --local

# 2. Work on your node in its source repo
#    Changes are immediately visible in ComfyUI (restart to reload)

# 3. Commit in source repo when ready
cd C:\code\smart-resolution-calc-repo\local
git add -A && git commit -m "Add feature"

# 4. Switch back to publish mode
cd C:\code\DazzleNodes\local
python scripts/dev_mode.py publish all

# 5. Update submodule pointer
cd nodes/smart-resolution-calc && git pull && cd ../..
git add nodes/smart-resolution-calc
git commit -m "Update smart-resolution-calc to latest"
```

### Safety Features

- **Automatic backups**: Timestamped backups in `nodes_bak/` before any destructive operation
- **Dry run**: `--dry-run` previews all operations without modifying anything
- **Windows symlinks**: Tries `mklink /D` first, falls back to `mklink /J` (junctions don't require admin)

---

## sync_web_files.py — Web Resource Sync

Collects JavaScript and CSS files from submodules into the unified `web/` directory that ComfyUI serves. Called automatically from `__init__.py` at startup.

```bash
python scripts/sync_web_files.py              # Auto-detect mode, use cache
python scripts/sync_web_files.py --mode=dev   # Force dev mode (symlinks)
python scripts/sync_web_files.py --mode=prod  # Force prod mode (copies)
python scripts/sync_web_files.py --force      # Skip cache check
python scripts/sync_web_files.py --quiet      # Suppress output
```

**Source priority:**
1. `web_src/core/` — shared libraries (highest priority)
2. `core_nodes/*/` — built-in nodes
3. `nodes/*/` — submodules or symlinks

**Output:** `web/*/` (gitignored, generated at runtime)

Uses an MD5 cache hash (`web/.sync_hash`) to skip re-syncing when nothing changed. Files are always **copied** (not symlinked) because ComfyUI's web server doesn't reliably follow symlinks.

For more on why web syncing is needed and the JavaScript depth detection pattern, see [dynamic-node-loading.md](dynamic-node-loading.md).

---

## sync-submodules.sh — Submodule Version Sync

Updates all submodules to their latest tagged release on `origin/main`, bumps the DazzleNodes patch version, and stages changes for commit.

```bash
./scripts/sync-submodules.sh                              # Update all
./scripts/sync-submodules.sh --dry-run                    # Preview updates
./scripts/sync-submodules.sh --only smart-resolution-calc # Update one
./scripts/sync-submodules.sh --only smart-resolution-calc --only fit-mask-to-image
```

**What it does:**
1. Fetches latest tags from each submodule's origin
2. Compares current commit to latest tag
3. Checks out the latest tag if behind
4. Bumps DazzleNodes PATCH version automatically
5. Stages all changes with a suggested commit message

> **Note:** Requires a clean working tree (no uncommitted changes).

---

## update-version.sh — Version String Updater

Updates the `__version__` string in `version.py` with branch, build count, date, and commit hash metadata.

```bash
./scripts/update-version.sh           # Auto-detect (dirty tree → today, clean → last commit date)
./scripts/update-version.sh --build   # Use today's date (for releases)
./scripts/update-version.sh --commit  # Use last commit date
./scripts/update-version.sh --auto    # Silent mode (for git hooks)
```

**Version format:** `MAJOR.MINOR.PATCH[-PHASE]_BRANCH_BUILD-YYYYMMDD-HASH`

Example: `0.4.0-alpha_main_42-20260127-3a789a6`

---

## install-hooks.sh — Git Hook Installer

Installs git hooks for automatic version tracking and branch protection.

```bash
./scripts/install-hooks.sh
```

**Two installation options:**

| Option | Hooks | Features |
|--------|-------|----------|
| Basic (not recommended) | `pre-commit` only | Version update only, no security |
| Standard (recommended) | `pre-commit`, `post-commit`, `pre-push` | Version update + branch protection + large file blocking + secret detection |

**Security features** (standard mode):
- Prevents committing private files to public branches
- Blocks secrets and credentials
- Enforces file size limits (>10MB)
- Automatic version tracking

Existing hooks are backed up with timestamps before replacement.

---

## fix_python_association.cmd — Windows Python Fix

Fixes the Windows file association when `.py` files open with the Microsoft Store Python stub instead of your real Python installation.

```cmd
REM Run as Administrator
scripts\fix_python_association.cmd
```

Sets `.py` files to use `C:\Python312\python.exe`. If you use a different Python installation path, edit the script first.

**Alternative:** Disable Windows Store Python stubs in Settings → Apps → App execution aliases → turn off `python.exe` and `python3.exe`.
