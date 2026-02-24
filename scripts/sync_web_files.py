#!/usr/bin/env python3
"""
Auto-sync web resources from nodes to web/ directory.

Sources (priority order):
- web_src/core/ (shared libraries)
- core_nodes/*/ (built-in nodes)
- nodes/*/ (submodules or symlinks)

Target:
- web/*/ (generated, gitignored)

Caching:
- Per-node content hashes stored in web/.sync_hashes.json
- Symlinked nodes (dev mode) always sync — dev files change frequently
- Submodule nodes only sync when content hash changes
- --force bypasses all cache checks

Usage:
    python sync_web_files.py              # Auto-detect, per-node caching
    python sync_web_files.py --force      # Skip all cache checks
    python sync_web_files.py --quiet      # Suppress output
    python sync_web_files.py --verbose    # Extra debug info
"""

import sys
import json
import shutil
from pathlib import Path
import argparse
import hashlib
import time

# ============================================================================
# Configuration
# ============================================================================

# Resolve project root relative to this script's location (scripts/ -> parent)
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent

# Web resource sources (priority order) — relative to project root
WEB_SOURCES = [
    ("web_src/core", "core"),           # Shared libraries (highest priority)
    ("core_nodes", "core_nodes"),       # Built-in nodes
    ("nodes", "nodes"),                 # Submodules/symlinks
]

# Cache file for per-node hashes
_HASH_FILE = ".sync_hashes.json"

# Legacy single-hash file (cleaned up on first run)
_LEGACY_HASH_FILE = ".sync_hash"

# ============================================================================
# Per-Node Hashing
# ============================================================================

def compute_node_hash(web_source_dir):
    """Compute content hash for a single node's web/ directory.

    Hashes every .js file's relative path and content. The relative path
    ensures the hash changes if files are renamed or reorganized, while
    keeping it stable across different machines (no absolute paths).

    Args:
        web_source_dir: Path to the node's web/ source directory

    Returns:
        str: MD5 hex digest of all .js files in the directory
    """
    hasher = hashlib.md5()
    for js_file in sorted(web_source_dir.rglob("**/*.js")):
        if js_file.is_file():
            rel = js_file.relative_to(web_source_dir)
            hasher.update(str(rel).encode())
            try:
                hasher.update(js_file.read_bytes())
            except Exception:
                pass
    return hasher.hexdigest()


def compute_core_hash(core_dir):
    """Compute content hash for web_src/core/ (flat .js files, no web/ subdir).

    Args:
        core_dir: Path to web_src/core/

    Returns:
        str: MD5 hex digest of all .js files
    """
    hasher = hashlib.md5()
    for js_file in sorted(core_dir.glob("*.js")):
        if js_file.is_file():
            hasher.update(js_file.name.encode())
            try:
                hasher.update(js_file.read_bytes())
            except Exception:
                pass
    return hasher.hexdigest()


def load_cached_hashes(web_dir):
    """Load per-node hash cache from .sync_hashes.json.

    Returns:
        dict: Mapping of node_name -> hash string
    """
    hash_file = web_dir / _HASH_FILE
    if not hash_file.exists():
        return {}
    try:
        return json.loads(hash_file.read_text())
    except Exception:
        return {}


def save_cached_hashes(web_dir, hashes):
    """Save per-node hash cache to .sync_hashes.json.

    Args:
        web_dir: Path to web/ directory
        hashes: dict mapping node_name -> hash string
    """
    hash_file = web_dir / _HASH_FILE
    hash_file.write_text(json.dumps(hashes, indent=2) + "\n")


def cleanup_legacy_hash(web_dir):
    """Remove legacy single-hash .sync_hash file if present."""
    legacy = web_dir / _LEGACY_HASH_FILE
    if legacy.exists():
        try:
            legacy.unlink()
        except Exception:
            pass

# ============================================================================
# Sync Logic
# ============================================================================

def sync_node_files(web_source, target_dir, verbose=False):
    """Copy all .js files from a node's web/ source to its target directory.

    Preserves directory structure for nested files (e.g., managers/, utils/).

    Args:
        web_source: Source web/ directory path
        target_dir: Target directory in web/<node_name>/
        verbose: Print debug info

    Returns:
        int: Number of files copied
    """
    copied = 0
    for js_file in web_source.rglob("**/*.js"):
        if not js_file.is_file():
            continue
        rel_path = js_file.relative_to(web_source)
        target_file = target_dir / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(js_file, target_file)
            copied += 1
            if verbose:
                print(f"    [COPY] {rel_path}")
        except Exception as e:
            if verbose:
                print(f"    [X] Failed: {rel_path} ({e})")
    return copied


def sync_web_files(mode=None, force=False, quiet=False, verbose=False):
    """Main sync function with per-node caching.

    Each node's web files are hashed independently. Only nodes with changed
    content are re-synced. Symlinked nodes (dev mode) always sync regardless
    of hash — dev files change frequently and sync is fast.

    Args:
        mode: Deprecated, ignored
        force: Skip all cache checks, sync everything
        quiet: Suppress output
        verbose: Extra debug output

    Returns:
        dict with sync stats
    """
    start_time = time.time()
    web_dir = _PROJECT_ROOT / "web"
    web_dir.mkdir(exist_ok=True)

    # Clean up legacy single-hash file on first run
    cleanup_legacy_hash(web_dir)

    cached_hashes = load_cached_hashes(web_dir)
    new_hashes = {}

    # Track stats
    synced_nodes = []
    skipped_nodes = []
    total_files = 0

    if not quiet:
        print("[DazzleNodes] Syncing web resources...")

    # Process each source
    for source_path_str, source_type in WEB_SOURCES:
        source_path = _PROJECT_ROOT / source_path_str
        if not source_path.exists():
            if verbose:
                print(f"  [Skip] {source_path} does not exist")
            continue

        # Special case: web_src/core (flat .js files, no web/ subdir)
        if source_type == "core" and source_path.name == "core":
            current_hash = compute_core_hash(source_path)
            new_hashes["_core"] = current_hash

            if not force and cached_hashes.get("_core") == current_hash:
                skipped_nodes.append("core")
                if verbose:
                    print(f"  [Core] Up-to-date (cached)")
                continue

            target_dir = web_dir / "core"
            # Remove stale target and recreate
            if target_dir.exists():
                shutil.rmtree(target_dir)
            target_dir.mkdir(exist_ok=True)

            core_files = 0
            for js_file in source_path.glob("*.js"):
                target_file = target_dir / js_file.name
                try:
                    shutil.copy2(js_file, target_file)
                    core_files += 1
                except Exception as e:
                    if verbose:
                        print(f"    [X] Failed: {js_file.name} ({e})")

            total_files += core_files
            synced_nodes.append("core")
            if not quiet:
                print(f"  [Core] Synced core library ({core_files} files)")
            continue

        # Normal case: scan for nodes with web/ directories
        if verbose:
            print(f"  [Scan] {source_path}")

        for node_dir in sorted(source_path.iterdir()):
            if not node_dir.is_dir():
                continue

            web_source = node_dir / "web"
            if not web_source.exists():
                if verbose:
                    print(f"    [Skip] {node_dir.name} (no web/)")
                continue

            node_name = node_dir.name
            is_symlink = node_dir.is_symlink()

            # Compute current content hash
            current_hash = compute_node_hash(web_source)
            new_hashes[node_name] = current_hash

            # Determine if this node needs syncing:
            # - force: always sync everything
            # - symlink (dev mode): always sync — dev files change frequently
            # - hash mismatch: content changed since last sync
            needs_update = force or is_symlink or (cached_hashes.get(node_name) != current_hash)

            if not needs_update:
                skipped_nodes.append(node_name)
                if verbose:
                    print(f"    [{source_type}] {node_name} — up-to-date (cached)")
                continue

            # Determine why we're syncing (for logging)
            if verbose or (not quiet and is_symlink):
                reason = "dev mode" if is_symlink else ("forced" if force else "changed")
                print(f"  [{source_type}] {node_name} — syncing ({reason})")

            # Remove stale target and recreate
            target_dir = web_dir / node_name
            if target_dir.exists():
                shutil.rmtree(target_dir)
            target_dir.mkdir(exist_ok=True)

            node_files = sync_node_files(web_source, target_dir, verbose=verbose)
            total_files += node_files
            synced_nodes.append(node_name)

            if not quiet and not verbose:
                if not is_symlink:
                    print(f"  [{source_type}] {node_name} ({node_files} files)")

    # Save updated per-node hashes
    save_cached_hashes(web_dir, new_hashes)

    elapsed = time.time() - start_time

    if not quiet:
        if synced_nodes:
            print(f"[DazzleNodes] Synced {len(synced_nodes)} node(s), "
                  f"{total_files} files in {elapsed:.2f}s")
            if skipped_nodes and verbose:
                print(f"[DazzleNodes] Skipped {len(skipped_nodes)} unchanged node(s): "
                      f"{', '.join(skipped_nodes)}")
        else:
            print(f"[DazzleNodes] All {len(skipped_nodes)} node(s) up-to-date (cached)")

    return {
        "cached": len(synced_nodes) == 0,
        "nodes": len(synced_nodes),
        "skipped": len(skipped_nodes),
        "files": total_files,
        "time": elapsed
    }

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sync DazzleNodes web resources (per-node caching)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sync_web_files.py                  # Use per-node cache
  python sync_web_files.py --force          # Skip all caches, sync everything
  python sync_web_files.py --quiet          # Suppress output
  python sync_web_files.py --verbose        # Extra debug info

Caching:
  - Submodule nodes: cached by content hash, only sync when changed
  - Symlinked nodes (dev mode): always sync, no cache check
  - Per-node hashes stored in web/.sync_hashes.json
        """
    )
    parser.add_argument("--force", action="store_true",
                        help="Skip all cache checks, sync everything")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress output")
    parser.add_argument("--verbose", action="store_true",
                        help="Extra debug output")

    args = parser.parse_args()

    try:
        stats = sync_web_files(
            force=args.force,
            quiet=args.quiet,
            verbose=args.verbose
        )

        if args.verbose and not args.quiet:
            print(f"\nSync Stats:")
            print(f"  All cached: {stats['cached']}")
            print(f"  Synced: {stats['nodes']}")
            print(f"  Skipped: {stats['skipped']}")
            print(f"  Files: {stats['files']}")
            print(f"  Time: {stats['time']:.3f}s")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
