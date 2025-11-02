#!/usr/bin/env python3
"""
DazzleNodes Development Mode Toggle Script

Manages switching between development mode (symlinks) and publish mode (git submodules)
for DazzleNodes custom node development.

Usage:
    python dev_mode.py status [--quick|--complete]
    python dev_mode.py dev [node|all]
    python dev_mode.py publish [node|all]

Global Options:
    -v, --verbose       Enable verbose output
    --dry-run          Show what would be done without making changes
    --no-backup        Skip backup creation (dangerous)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shutil
import yaml
import os

# ============================================================================
# Configuration and Constants
# ============================================================================

# Node mappings: directory name -> source repository path
NODE_MAPPINGS = {
    "smart-resolution-calc": r"C:\code\smart-resolution-calc-repo\local",
    "fit-mask-to-image": r"C:\code\ComfyUI-ImageMask-Fix\local"
}

# Default configuration
DEFAULT_CONFIG = {
    "status_default_mode": "quick",  # "quick" or "complete"
    "backup_enabled": True,
    "verbose": False
}

# ============================================================================
# Configuration Loading
# ============================================================================

def load_config():
    """Load configuration from YAML file, environment variables, and defaults."""
    config = DEFAULT_CONFIG.copy()

    # Try to load config file
    config_file = Path(__file__).parent / "dev_mode_config.yaml"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f) or {}
                config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")

    # Environment variables override config file
    if os.environ.get("DEV_MODE_STATUS_DEFAULT"):
        config["status_default_mode"] = os.environ["DEV_MODE_STATUS_DEFAULT"]
    if os.environ.get("DEV_MODE_VERBOSE"):
        config["verbose"] = os.environ["DEV_MODE_VERBOSE"].lower() in ("1", "true", "yes")

    return config

# ============================================================================
# Helper Functions
# ============================================================================

def get_dazzlenodes_root():
    """Get the DazzleNodes root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent

def is_symlink(path):
    """
    Check if path is a symlink or junction on Windows.

    Args:
        path: Path to check

    Returns:
        bool: True if path is a symlink/junction
    """
    path = Path(path)
    if not path.exists():
        return False

    # On Windows, check for both symlinks and junctions
    if sys.platform == "win32":
        try:
            # Use dir /AL to check for symlinks/junctions
            result = subprocess.run(
                ["cmd", "/c", "dir", "/AL", str(path.parent)],
                capture_output=True,
                text=True
            )
            return path.name in result.stdout
        except Exception:
            # Fallback to pathlib check
            return path.is_symlink()
    else:
        return path.is_symlink()

def backup_node(node_path, verbose=False):
    """
    Backup a node directory to nodes_bak/ with timestamp.

    Args:
        node_path: Path to node directory to backup
        verbose: Enable verbose output

    Returns:
        Path: Backup directory path if successful, None otherwise
    """
    node_path = Path(node_path)
    if not node_path.exists():
        return None

    # Create backup directory with timestamp
    root = get_dazzlenodes_root()
    backup_root = root / "nodes_bak"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{node_path.name}_{timestamp}"
    backup_path = backup_root / backup_name

    try:
        backup_root.mkdir(exist_ok=True)

        if verbose:
            print(f"  Backing up {node_path.name} to {backup_path}")

        # Copy the directory (handles both real dirs and symlinks)
        if is_symlink(node_path):
            # For symlinks, just note it in a file
            backup_path.mkdir()
            link_target = node_path.resolve()
            with open(backup_path / "SYMLINK_INFO.txt", "w") as f:
                f.write(f"This was a symlink to: {link_target}\n")
        else:
            shutil.copytree(node_path, backup_path, symlinks=True)

        if verbose:
            print(f"  [OK] Backup created: {backup_path}")

        return backup_path

    except Exception as e:
        print(f"  [X] Backup failed: {e}")
        return None

def create_symlink(target, link_path, verbose=False):
    """
    Create a directory symlink on Windows using mklink.
    Falls back to junction if symlink creation fails.

    Args:
        target: Target directory path
        link_path: Symlink path to create
        verbose: Enable verbose output

    Returns:
        bool: True if successful
    """
    target = Path(target).resolve()
    link_path = Path(link_path)

    if not target.exists():
        print(f"  [X] Target does not exist: {target}")
        return False

    if link_path.exists():
        print(f"  [X] Link path already exists: {link_path}")
        return False

    try:
        # Try mklink /D first (requires admin on some systems)
        if verbose:
            print(f"  Creating symlink: {link_path} -> {target}")

        result = subprocess.run(
            ["cmd", "/c", "mklink", "/D", str(link_path), str(target)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            if verbose:
                print(f"  [OK] Symlink created successfully")
            return True

        # Fallback to junction (no admin required)
        if verbose:
            print(f"  Symlink failed, trying junction...")

        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link_path), str(target)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            if verbose:
                print(f"  [OK] Junction created successfully")
            return True

        print(f"  [X] Failed to create link: {result.stderr}")
        return False

    except Exception as e:
        print(f"  [X] Exception creating link: {e}")
        return False

def remove_path(path, verbose=False):
    """
    Remove a file, directory, symlink, or junction.

    Args:
        path: Path to remove
        verbose: Enable verbose output

    Returns:
        bool: True if successful
    """
    path = Path(path)
    if not path.exists():
        return True

    try:
        if verbose:
            print(f"  Removing: {path}")

        if is_symlink(path):
            # For symlinks/junctions, just remove the link
            if sys.platform == "win32":
                subprocess.run(["cmd", "/c", "rmdir", str(path)], check=True)
            else:
                path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

        if verbose:
            print(f"  [OK] Removed successfully")

        return True

    except Exception as e:
        print(f"  [X] Failed to remove: {e}")
        return False

# ============================================================================
# Git Operations
# ============================================================================

def get_git_status(repo_path, verbose=False):
    """
    Get git status for a repository.

    Args:
        repo_path: Path to git repository
        verbose: Enable verbose output

    Returns:
        dict: Git status information
    """
    repo_path = Path(repo_path)
    if not (repo_path / ".git").exists():
        return {"error": "Not a git repository"}

    try:
        # Get current branch
        result = subprocess.run(
            ["git", "-C", str(repo_path), "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()

        # Get status
        result = subprocess.run(
            ["git", "-C", str(repo_path), "status", "--short"],
            capture_output=True,
            text=True,
            check=True
        )
        status = result.stdout.strip()

        # Get latest commit
        result = subprocess.run(
            ["git", "-C", str(repo_path), "log", "-1", "--oneline"],
            capture_output=True,
            text=True,
            check=True
        )
        commit = result.stdout.strip()

        return {
            "branch": branch,
            "status": status,
            "commit": commit,
            "has_changes": bool(status)
        }

    except Exception as e:
        if verbose:
            print(f"  Git status error: {e}")
        return {"error": str(e)}

# ============================================================================
# Status Command
# ============================================================================

def cmd_status(args, config):
    """Show status of all nodes (quick or complete mode)."""
    root = get_dazzlenodes_root()
    nodes_dir = root / "nodes"

    # Determine mode
    mode = "complete" if args.complete else ("quick" if args.quick else config["status_default_mode"])

    print(f"\n{'='*70}")
    print(f"DazzleNodes Status ({mode} mode)")
    print(f"{'='*70}\n")
    print(f"Root: {root}\n")

    # Check each node
    for node_name, source_path in NODE_MAPPINGS.items():
        node_path = nodes_dir / node_name
        source_path = Path(source_path)

        print(f"[*] {node_name}")
        print(f"   {'-'*65}")

        # Check existence
        exists = node_path.exists()
        is_link = is_symlink(node_path) if exists else False

        if not exists:
            print(f"   Status: [X] MISSING")
            print(f"   Expected: {node_path}")
        elif is_link:
            print(f"   Status: [L] DEV MODE (symlink)")
            print(f"   Target: {node_path.resolve()}")

            if mode == "complete":
                git_info = get_git_status(source_path, args.verbose)
                if "error" not in git_info:
                    print(f"   Branch: {git_info['branch']}")
                    print(f"   Commit: {git_info['commit']}")
                    if git_info['has_changes']:
                        print(f"   Changes: [!] UNCOMMITTED CHANGES")
                        if args.verbose:
                            print(f"\n   Git Status:")
                            for line in git_info['status'].split('\n'):
                                print(f"      {line}")
                    else:
                        print(f"   Changes: [OK] Clean")
        else:
            print(f"   Status: [D] PUBLISH MODE (submodule)")
            print(f"   Path: {node_path}")

            if mode == "complete":
                git_info = get_git_status(node_path, args.verbose)
                if "error" not in git_info:
                    print(f"   Branch: {git_info['branch']}")
                    print(f"   Commit: {git_info['commit']}")
                    if git_info['has_changes']:
                        print(f"   Changes: [!] UNCOMMITTED CHANGES")
                    else:
                        print(f"   Changes: [OK] Clean")

        # Check source repository
        if source_path.exists():
            print(f"   Source: [OK] {source_path}")
            if mode == "complete" and not is_link:
                source_git = get_git_status(source_path, args.verbose)
                if "error" not in source_git and source_git['has_changes']:
                    print(f"   Source has uncommitted changes!")
        else:
            print(f"   Source: [X] NOT FOUND")

        print()

    print(f"{'='*70}\n")

# ============================================================================
# Dev Command
# ============================================================================

def cmd_dev(args, config):
    """Switch node(s) to dev mode (symlinks)."""
    root = get_dazzlenodes_root()
    nodes_dir = root / "nodes"

    # Determine which nodes to process
    if args.node == "all":
        nodes_to_process = list(NODE_MAPPINGS.keys())
    elif args.node in NODE_MAPPINGS:
        nodes_to_process = [args.node]
    else:
        print(f"Error: Unknown node '{args.node}'")
        print(f"Available nodes: {', '.join(NODE_MAPPINGS.keys())}")
        return 1

    print(f"\n{'='*70}")
    print(f"Switching to DEV MODE")
    print(f"{'='*70}\n")

    if args.dry_run:
        print("[DRY-RUN] - No changes will be made\n")

    success_count = 0
    for node_name in nodes_to_process:
        node_path = nodes_dir / node_name
        source_path = Path(NODE_MAPPINGS[node_name])

        print(f"Processing: {node_name}")

        # Check if already in dev mode
        if node_path.exists() and is_symlink(node_path):
            print(f"  [i]Already in dev mode (symlink exists)")
            success_count += 1
            continue

        # Check source exists
        if not source_path.exists():
            print(f"  [X] Source not found: {source_path}")
            continue

        # Backup if requested and path exists
        if node_path.exists() and not args.no_backup and config["backup_enabled"]:
            if not args.dry_run:
                backup_path = backup_node(node_path, args.verbose)
                if not backup_path:
                    print(f"  [X] Backup failed, aborting")
                    continue
            else:
                print(f"  Would backup to: nodes_bak/{node_name}_[timestamp]")

        # Remove existing path
        if node_path.exists():
            if not args.dry_run:
                if not remove_path(node_path, args.verbose):
                    print(f"  [X] Failed to remove existing path")
                    continue
            else:
                print(f"  Would remove: {node_path}")

        # Create symlink
        if not args.dry_run:
            if create_symlink(source_path, node_path, args.verbose):
                print(f"  [OK] Switched to dev mode")
                success_count += 1
            else:
                print(f"  [X] Failed to create symlink")
        else:
            print(f"  Would create symlink: {node_path} -> {source_path}")
            success_count += 1

        print()

    print(f"{'='*70}")
    print(f"Result: {success_count}/{len(nodes_to_process)} nodes switched to dev mode")
    print(f"{'='*70}\n")

    return 0 if success_count == len(nodes_to_process) else 1

# ============================================================================
# Publish Command
# ============================================================================

def cmd_publish(args, config):
    """Switch node(s) to publish mode (submodules)."""
    root = get_dazzlenodes_root()
    nodes_dir = root / "nodes"

    # Determine which nodes to process
    if args.node == "all":
        nodes_to_process = list(NODE_MAPPINGS.keys())
    elif args.node in NODE_MAPPINGS:
        nodes_to_process = [args.node]
    else:
        print(f"Error: Unknown node '{args.node}'")
        print(f"Available nodes: {', '.join(NODE_MAPPINGS.keys())}")
        return 1

    print(f"\n{'='*70}")
    print(f"Switching to PUBLISH MODE")
    print(f"{'='*70}\n")

    if args.dry_run:
        print("[DRY-RUN] - No changes will be made\n")

    success_count = 0
    for node_name in nodes_to_process:
        node_path = nodes_dir / node_name

        print(f"Processing: {node_name}")

        # Check if already in publish mode (not a symlink)
        if node_path.exists() and not is_symlink(node_path):
            print(f"  [i]Already in publish mode (submodule)")
            success_count += 1
            continue

        # Backup if symlink exists
        if node_path.exists() and not args.no_backup and config["backup_enabled"]:
            if not args.dry_run:
                backup_path = backup_node(node_path, args.verbose)
                if not backup_path:
                    print(f"  [X] Backup failed, aborting")
                    continue
            else:
                print(f"  Would backup symlink info to: nodes_bak/{node_name}_[timestamp]")

        # Remove symlink
        if node_path.exists():
            if not args.dry_run:
                if not remove_path(node_path, args.verbose):
                    print(f"  [X] Failed to remove symlink")
                    continue
            else:
                print(f"  Would remove symlink: {node_path}")

        # Restore submodule with git
        if not args.dry_run:
            try:
                # Use relative path from root: nodes/node-name
                submodule_path = f"nodes/{node_name}"
                result = subprocess.run(
                    ["git", "-C", str(root), "submodule", "update", "--init", submodule_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"  [OK] Restored submodule")
                if args.verbose:
                    print(f"     {result.stdout.strip()}")
                success_count += 1
            except subprocess.CalledProcessError as e:
                print(f"  [X] Failed to restore submodule: {e.stderr}")
        else:
            print(f"  Would run: git submodule update --init nodes/{node_name}")
            success_count += 1

        print()

    print(f"{'='*70}")
    print(f"Result: {success_count}/{len(nodes_to_process)} nodes switched to publish mode")
    print(f"{'='*70}\n")

    return 0 if success_count == len(nodes_to_process) else 1

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point."""
    # Load configuration
    config = load_config()

    # Create main parser
    parser = argparse.ArgumentParser(
        description="DazzleNodes Development Mode Toggle Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dev_mode.py status                       # Quick status (default)
  python dev_mode.py status --complete            # Detailed status with git info
  python dev_mode.py dev smart-resolution-calc    # Switch one node to dev mode
  python dev_mode.py dev all                      # Switch all nodes to dev mode
  python dev_mode.py publish all                  # Restore all submodules
  python dev_mode.py -v dev all                   # Verbose mode
  python dev_mode.py --dry-run publish all        # Show what would be done
        """
    )

    # Global options
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip backup creation (dangerous)")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Status command
    status_parser = subparsers.add_parser("status",
                                          help="Show current status of all nodes")
    status_group = status_parser.add_mutually_exclusive_group()
    status_group.add_argument("--quick", action="store_true",
                             help="Quick status (default)")
    status_group.add_argument("--complete", action="store_true",
                             help="Complete status with git information")

    # Dev command
    dev_parser = subparsers.add_parser("dev",
                                       help="Switch node(s) to dev mode (symlinks)")
    dev_parser.add_argument("node", nargs="?",
                           help="Node name or 'all' (required)")

    # Publish command
    publish_parser = subparsers.add_parser("publish",
                                          help="Switch node(s) to publish mode (submodules)")
    publish_parser.add_argument("node", nargs="?",
                               help="Node name or 'all' (required)")

    # Parse arguments
    args = parser.parse_args()

    # Override config with command line args
    if args.verbose:
        config["verbose"] = True
    if args.no_backup:
        config["backup_enabled"] = False

    # Execute command
    if args.command == "status":
        return cmd_status(args, config)
    elif args.command == "dev":
        if not args.node:
            print("Error: Node name required")
            print(f"Usage: python dev_mode.py dev [node|all]")
            print(f"Available nodes: {', '.join(NODE_MAPPINGS.keys())}")
            return 1
        return cmd_dev(args, config)
    elif args.command == "publish":
        if not args.node:
            print("Error: Node name required")
            print(f"Usage: python dev_mode.py publish [node|all]")
            print(f"Available nodes: {', '.join(NODE_MAPPINGS.keys())}")
            return 1
        return cmd_publish(args, config)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
