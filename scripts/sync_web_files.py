#!/usr/bin/env python3
"""
Auto-sync web resources from nodes to web/ directory.

Sources (priority order):
- web_src/core/ (shared libraries)
- core_nodes/*/ (built-in nodes)
- nodes/*/ (submodules or symlinks)

Target:
- web/*/ (generated, gitignored)

Usage:
    python sync_web_files.py              # Auto-detect mode, use cache
    python sync_web_files.py --mode=dev   # Force dev mode (symlinks)
    python sync_web_files.py --mode=prod  # Force prod mode (copies)
    python sync_web_files.py --force      # Skip cache check
    python sync_web_files.py --quiet      # Suppress output
"""

import sys
import shutil
from pathlib import Path
import argparse
import hashlib
import time

# ============================================================================
# Configuration
# ============================================================================

# Web resource sources (priority order)
WEB_SOURCES = [
    ("web_src/core", "core"),           # Shared libraries (highest priority)
    ("core_nodes", "core_nodes"),       # Built-in nodes
    ("nodes", "nodes"),                 # Submodules/symlinks
]

# ============================================================================
# Mode Detection
# ============================================================================

def detect_dev_mode():
    """
    Detect if we're in dev or prod mode by checking if nodes/* are symlinks.

    Returns:
        "dev" if ANY node is a symlink (development workflow)
        "prod" if ALL nodes are real directories (production/submodule workflow)
    """
    nodes_dir = Path("nodes")
    if not nodes_dir.exists():
        return "prod"  # Default

    # Check ALL nodes - if ANY is a symlink, we're in dev mode
    has_symlink = False
    has_real_dir = False

    for node_dir in nodes_dir.iterdir():
        if node_dir.is_dir():
            if node_dir.is_symlink():
                has_symlink = True
            else:
                has_real_dir = True

    # If ANY node is a symlink, treat as dev mode
    # (Allows mixed state during transition)
    return "dev" if has_symlink else "prod"

# ============================================================================
# Caching (avoid unnecessary syncs)
# ============================================================================

def compute_source_hash(source_dirs):
    """Compute hash of all source web files for change detection."""
    hasher = hashlib.md5()

    for source_dir, _ in source_dirs:
        source_path = Path(source_dir)
        if not source_path.exists():
            continue

        # Hash all .js files in web/ subdirectories
        for js_file in sorted(source_path.rglob("web/**/*.js")):
            if js_file.is_file():
                hasher.update(str(js_file).encode())
                try:
                    hasher.update(js_file.read_bytes())
                except:
                    pass  # Skip unreadable files

        # Also hash direct .js files in web_src/core (no web/ subdir)
        if source_path.name == "core" and source_path.parent.name == "web_src":
            for js_file in sorted(source_path.glob("*.js")):
                if js_file.is_file():
                    hasher.update(str(js_file).encode())
                    try:
                        hasher.update(js_file.read_bytes())
                    except:
                        pass

    return hasher.hexdigest()

def needs_sync(web_dir, source_hash):
    """Check if sync needed by comparing hashes."""
    hash_file = web_dir / ".sync_hash"

    if not hash_file.exists():
        return True  # First sync

    try:
        cached_hash = hash_file.read_text().strip()
        return cached_hash != source_hash
    except Exception as e:
        print(f"[DazzleNodes] Warning: Could not read sync hash ({e}), forcing sync")
        return True  # Assume sync needed on error

def save_sync_hash(web_dir, source_hash):
    """Save current source hash."""
    hash_file = web_dir / ".sync_hash"
    hash_file.write_text(source_hash)

# ============================================================================
# Sync Logic
# ============================================================================

def create_link_or_copy(source_file, target_file, use_symlink=True, verbose=False):
    """
    Create symlink to source file, or copy if symlink fails.

    Args:
        source_file: Source file path
        target_file: Target file path
        use_symlink: Try to create symlink (True) or just copy (False)
        verbose: Print debug info

    Returns:
        "symlink", "copy", or "failed"
    """
    if not source_file.exists() or not source_file.is_file():
        if verbose:
            print(f"    [!] Source not found: {source_file}")
        return "failed"

    if use_symlink:
        try:
            # Try creating symlink with relative path
            target_file.symlink_to(source_file)
            if verbose:
                print(f"    [LINK] Symlinked: {target_file.name}")
            return "symlink"
        except (OSError, NotImplementedError) as e:
            if verbose:
                print(f"    [!] Symlink failed ({e}), copying instead")
            # Fall through to copy

    # Copy file
    try:
        shutil.copy2(source_file, target_file)
        if verbose:
            print(f"    [COPY] Copied: {target_file.name}")
        return "copy"
    except Exception as e:
        if verbose:
            print(f"    [X] Copy failed: {e}")
        return "failed"

def sync_web_files(mode=None, force=False, quiet=False, verbose=False):
    """
    Main sync function.

    Args:
        mode: Deprecated, ignored (always copies files for ComfyUI compatibility)
        force: Skip cache check, always sync
        quiet: Suppress output
        verbose: Extra debug output

    Returns:
        dict with sync stats
    """
    start_time = time.time()
    web_dir = Path("web")

    # Note: Always copy files (ComfyUI web server doesn't follow symlinks)
    if not quiet:
        print(f"[DazzleNodes] Syncing web resources...")

    # Check if sync needed (unless forced)
    source_hash = compute_source_hash(WEB_SOURCES)
    if not force:
        if not needs_sync(web_dir, source_hash):
            if not quiet:
                print("[DazzleNodes] Web resources up-to-date (cached)")
            return {
                "cached": True,
                "nodes": 0,
                "files": 0,
                "time": time.time() - start_time
            }

    # Create web directory if needed
    web_dir.mkdir(exist_ok=True)

    # Create temp directory for atomic operation
    temp_dir = web_dir / ".sync_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    # Track seen node names (prevent duplicates)
    seen_nodes = {}
    total_files = 0
    copy_count = 0

    # Process each source
    for source_path_str, source_type in WEB_SOURCES:
        source_path = Path(source_path_str)

        if not source_path.exists():
            if verbose:
                print(f"  [Skip] {source_path} does not exist")
            continue

        # Special case: web_src/core has .js files directly (no web/ subdir)
        if source_type == "core" and source_path.name == "core":
            if verbose:
                print(f"  [Core] Processing {source_path}")

            target_dir = temp_dir / "core"
            target_dir.mkdir(exist_ok=True)

            for js_file in source_path.glob("*.js"):
                target_file = target_dir / js_file.name

                # Always copy (ComfyUI web server doesn't follow symlinks)
                result = create_link_or_copy(
                    js_file,
                    target_file,
                    use_symlink=False,
                    verbose=verbose
                )

                if result == "copy":
                    copy_count += 1
                    total_files += 1

            if not quiet and total_files > 0:
                print(f"  [Core] Synced core library ({total_files} files)")

            continue

        # Normal case: scan for nodes with web/ directories
        if verbose:
            print(f"  [Scan] {source_path}")

        for node_dir in source_path.iterdir():
            if not node_dir.is_dir():
                continue

            # Check for web/ subdirectory
            web_source = node_dir / "web"
            if not web_source.exists():
                if verbose:
                    print(f"    [Skip] {node_dir.name} (no web/)")
                continue

            node_name = node_dir.name

            # Check for duplicate names across sources
            if node_name in seen_nodes:
                print(f"\n[DazzleNodes] ERROR: Duplicate node name '{node_name}'")
                print(f"  Source 1: {seen_nodes[node_name]}")
                print(f"  Source 2: {node_dir}")
                print(f"\nPlease rename one of these nodes to avoid conflicts.")
                sys.exit(1)

            seen_nodes[node_name] = str(node_dir)

            # Create target directory and copy files
            # (Always copy - ComfyUI web server doesn't follow symlinks)
            target_dir = temp_dir / node_name
            target_dir.mkdir(exist_ok=True)

            node_files = 0

            # Use rglob to recursively find all .js files in subdirectories
            for js_file in web_source.rglob("**/*.js"):
                # Preserve directory structure relative to web_source
                rel_path = js_file.relative_to(web_source)
                target_file = target_dir / rel_path

                # Create parent directories if needed (e.g., managers/, utils/)
                target_file.parent.mkdir(parents=True, exist_ok=True)

                result = create_link_or_copy(
                    js_file,
                    target_file,
                    use_symlink=False,
                    verbose=verbose
                )

                if result == "copy":
                    copy_count += 1
                    node_files += 1

            total_files += node_files

            if not quiet and node_files > 0:
                print(f"  [{source_type}] {node_name} ({node_files} files)")

    # Atomic replace: Move temp to final location
    old_dir = web_dir / ".sync_old"
    if old_dir.exists():
        shutil.rmtree(old_dir)
    old_dir.mkdir()

    # Move current web/* to .sync_old (preserve README.md, .sync_hash)
    for item in web_dir.iterdir():
        if item.name not in [".sync_temp", ".sync_hash", ".sync_old", "README.md"]:
            try:
                item.rename(old_dir / item.name)
            except:
                pass  # Ignore errors, will be overwritten

    # Move temp contents to web/
    for item in temp_dir.iterdir():
        try:
            item.rename(web_dir / item.name)
        except Exception as e:
            if not quiet:
                print(f"  [!] Failed to move {item.name}: {e}")

    # Cleanup
    try:
        temp_dir.rmdir()
    except:
        pass

    if old_dir.exists():
        try:
            shutil.rmtree(old_dir)
        except:
            pass

    # Save hash
    save_sync_hash(web_dir, source_hash)

    elapsed = time.time() - start_time

    if not quiet:
        print(f"[DazzleNodes] Synced {len(seen_nodes)} nodes, {total_files} files ({copy_count} copies) in {elapsed:.2f}s")

    return {
        "cached": False,
        "nodes": len(seen_nodes),
        "files": total_files,
        "copies": copy_count,
        "time": elapsed
    }

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sync DazzleNodes web resources (always copies files)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sync_web_files.py                  # Use cache, sync only if changed
  python sync_web_files.py --force          # Skip cache, always sync
  python sync_web_files.py --quiet          # Suppress output
  python sync_web_files.py --verbose        # Extra debug info

Note: Always copies files (ComfyUI web server doesn't follow symlinks)
        """
    )
    parser.add_argument("--force", action="store_true", help="Skip cache check, always sync")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    parser.add_argument("--verbose", action="store_true", help="Extra debug output")

    args = parser.parse_args()

    try:
        stats = sync_web_files(
            force=args.force,
            quiet=args.quiet,
            verbose=args.verbose
        )

        if args.verbose and not args.quiet:
            print(f"\nSync Stats:")
            print(f"  Cached: {stats['cached']}")
            print(f"  Nodes: {stats['nodes']}")
            print(f"  Files: {stats['files']}")
            if not stats['cached']:
                print(f"  Copies: {stats.get('copies', 0)}")
            print(f"  Time: {stats['time']:.3f}s")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
