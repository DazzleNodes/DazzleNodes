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

## File Sync Behavior

The sync script always **copies** files (ComfyUI's web server doesn't follow symlinks):

- Files in `web/` are copies of sources
- Hash-based caching prevents unnecessary re-syncs
- Auto-sync runs on ComfyUI startup
- Manual sync with `python scripts/sync_web_files.py --force` after editing source files

## Caching

The sync script uses MD5 hashing of all source files to detect changes:
- **If sources unchanged**: Skips sync (fast startup)
- **If sources changed**: Re-syncs all files
- **Force sync**: `python scripts/sync_web_files.py --force`

## Manual Sync

You can manually trigger a sync after editing source files:

```bash
cd C:\code\DazzleNodes\local

# Use cache (only sync if files changed)
python scripts/sync_web_files.py

# Force sync (ignore cache)
python scripts/sync_web_files.py --force

# Verbose output
python scripts/sync_web_files.py --verbose

# Quiet mode (for scripts)
python scripts/sync_web_files.py --quiet
```

## Troubleshooting

### JavaScript Not Loading

1. Check if auto-sync ran: Look for `[DazzleNodes]` messages in ComfyUI console
2. Force sync: `python scripts/sync_web_files.py --force --verbose`
3. Check source files exist:
   - `nodes/smart-resolution-calc/web/` (should have .js files)
   - `web_src/core/` (if using shared libraries)

### Changes Not Visible After Editing Source Files

1. Force sync: `python scripts/sync_web_files.py --force`
2. Restart ComfyUI completely
3. Check browser console for JavaScript errors
4. Clear browser cache (Ctrl+Shift+R)

## Architecture Details

For complete architecture documentation, see:
- `private/claude/2025-11-02__09-15-35__auto-sync-web-architecture-with-core-nodes.md`

## Questions?

Check the main DazzleNodes README or scripts/README.md for more information
