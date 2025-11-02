# DazzleNodes Web Resources (Auto-Generated)

**⚠️ DO NOT EDIT FILES IN THIS DIRECTORY**

This directory is **automatically generated** when ComfyUI loads DazzleNodes.

## How It Works

When ComfyUI imports DazzleNodes (`__init__.py`), it runs `scripts/sync_web_files.py` to automatically sync JavaScript files from their source locations to this directory.

## Source Locations (Priority Order)

1. **`web_src/core/`** - Shared JavaScript libraries (highest priority)
2. **`core_nodes/*/web/`** - Built-in DazzleNodes nodes
3. **`nodes/*/web/`** - Git submodule nodes (lowest priority)

## Directory Structure

```
web/
├── README.md           # This file (committed to git)
├── .sync_hash          # Cache file (gitignored)
├── core/               # Shared libraries (gitignored)
│   └── *.js
└── node-name/          # Per-node JavaScript (gitignored)
    └── *.js
```

## Dev vs Prod Mode

The sync script automatically detects your environment:

- **Dev Mode** (symlinks): Files in `web/` are symlinks to sources
  - Changes in source repos immediately visible
  - Detected by checking if `nodes/*` are symlinks

- **Prod Mode** (copies): Files in `web/` are copies of sources
  - Stable, isolated from source changes
  - Standard git submodule setup

## Caching

The sync script uses MD5 hashing of all source files to detect changes:
- **If sources unchanged**: Skips sync (fast startup)
- **If sources changed**: Re-syncs all files
- **Force sync**: `python scripts/sync_web_files.py --force`

## Manual Sync

You can manually trigger a sync:

```bash
cd C:\code\DazzleNodes\local

# Auto-detect mode, use cache
python scripts/sync_web_files.py

# Force sync (ignore cache)
python scripts/sync_web_files.py --force

# Force dev mode (symlinks)
python scripts/sync_web_files.py --mode=dev

# Force prod mode (copies)
python scripts/sync_web_files.py --mode=prod

# Verbose output
python scripts/sync_web_files.py --verbose
```

## Troubleshooting

### JavaScript Not Loading

1. Check if auto-sync ran: Look for `[DazzleNodes]` messages in ComfyUI console
2. Force sync: `python scripts/sync_web_files.py --force --verbose`
3. Check source files exist:
   - `nodes/smart-resolution-calc/web/` (should have .js files)
   - `web_src/core/` (if using shared libraries)

### Changes Not Visible (Dev Mode)

1. Verify dev mode: `python scripts/dev_mode.py status`
2. Check symlinks: `dir C:\code\DazzleNodes\local\web /AL`
3. Restart ComfyUI completely

### Changes Not Visible (Prod Mode)

1. Commit changes in source repository
2. Update submodule: `cd nodes/node-name && git pull`
3. Force sync: `python scripts/sync_web_files.py --force`
4. Restart ComfyUI

## Architecture Details

For complete architecture documentation, see:
- `private/claude/2025-11-02__09-15-35__auto-sync-web-architecture-with-core-nodes.md`

## Questions?

Check the main DazzleNodes README or scripts/README.md for more information
