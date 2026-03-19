"""
@author: djdarcy
@title: DazzleNodes
@nickname: DazzleNodes
@description: Collection of productivity custom nodes for ComfyUI workflows
"""

import sys
import importlib.util
import json
import subprocess
from pathlib import Path

# Import version information
from .version import __version__, VERSION, BASE_VERSION, PIP_VERSION

# ============================================================================
# Auto-sync web resources
# ============================================================================
def _sync_web_resources():
    """Sync web resources from submodules and core nodes to web/ directory."""
    sync_script = Path(__file__).parent / "scripts" / "sync_web_files.py"

    print("[DazzleNodes] Starting web resource sync...")
    print(f"[DazzleNodes] Sync script path: {sync_script}")
    print(f"[DazzleNodes] Sync script exists: {sync_script.exists()}")

    if not sync_script.exists():
        print(f"[DazzleNodes] ERROR: sync_web_files.py not found at {sync_script}")
        return

    try:
        print(f"[DazzleNodes] Executing: {sys.executable} {sync_script}")
        result = subprocess.run(
            [sys.executable, str(sync_script)],  # Removed --quiet to see output
            capture_output=True,
            text=True,
            timeout=30,  # Increased from 10s
            check=False,
            cwd=Path(__file__).parent  # CRITICAL: Set working directory to DazzleNodes directory
        )

        # Always show stdout
        if result.stdout:
            print("[DazzleNodes] Sync output:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"[DazzleNodes]   {line}")

        # Check result
        if result.returncode == 0:
            print("[DazzleNodes] [OK] Web resource sync completed successfully")
        else:
            print(f"[DazzleNodes] [FAIL] Web sync failed with exit code {result.returncode}")
            if result.stderr:
                print(f"[DazzleNodes] Error output:")
                for line in result.stderr.strip().split('\n'):
                    if line:
                        print(f"[DazzleNodes]   {line}")

    except subprocess.TimeoutExpired:
        print("[DazzleNodes] ERROR: Web sync timed out after 30 seconds")
    except Exception as e:
        print(f"[DazzleNodes] ERROR: Web sync exception: {type(e).__name__}: {e}")

# ============================================================================
# Auto-initialize empty submodules (e.g., after ComfyUI Manager install)
# ============================================================================
def _find_empty_submodule_dirs(nodes_dir):
    """Return list of submodule directory names that are empty or contain only .git file."""
    empty = []
    for child in nodes_dir.iterdir():
        if not child.is_dir():
            continue
        # Skip symlinks/junctions (dev mode)
        try:
            if child.is_symlink() or child.is_junction():
                continue
        except AttributeError:
            # is_junction() added in Python 3.12
            if child.is_symlink():
                continue
        # Skip disabled nodes (set by dev_mode.py disable command)
        if (child / "DISABLED").exists():
            continue
        # Check if directory is empty (or only contains .git file)
        contents = list(child.iterdir())
        if len(contents) == 0 or (len(contents) == 1 and contents[0].name == ".git"):
            empty.append(child.name)
    return empty


def _parse_gitmodules(base_dir):
    """Parse .gitmodules file and return dict mapping submodule paths to URLs."""
    gitmodules_path = base_dir / ".gitmodules"
    if not gitmodules_path.exists():
        return {}

    modules = {}
    current_path = None
    current_url = None

    for line in gitmodules_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("path = "):
            current_path = line[len("path = "):]
        elif line.startswith("url = "):
            current_url = line[len("url = "):]
        if current_path and current_url:
            modules[current_path] = current_url
            current_path = None
            current_url = None

    return modules


def _load_submodule_versions(base_dir):
    """Load pinned submodule versions from submodule_versions.json."""
    versions_path = base_dir / "submodule_versions.json"
    if not versions_path.exists():
        return {}
    try:
        return json.loads(versions_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"[DazzleNodes] [WARN] Could not read submodule_versions.json: {e}")
        return {}


def _clone_submodules_fallback(base_dir, empty_submodules):
    """Fallback: clone submodules directly when git submodule update doesn't work.

    Used when installed from a tarball/registry (no .git directory).
    Reads URLs from .gitmodules and pinned versions from submodule_versions.json.
    """
    modules = _parse_gitmodules(base_dir)
    versions = _load_submodule_versions(base_dir)

    if not modules:
        print("[DazzleNodes] [WARN] No .gitmodules found — cannot clone submodules")
        return False

    success_count = 0
    fail_count = 0

    for submodule_name in empty_submodules:
        submodule_path = f"nodes/{submodule_name}"
        url = modules.get(submodule_path)
        if not url:
            print(f"[DazzleNodes] [WARN] No URL found for {submodule_name} in .gitmodules")
            fail_count += 1
            continue

        target_dir = base_dir / submodule_path
        version = versions.get(submodule_path)

        # Build clone command
        clone_cmd = ["git", "clone", "--depth", "1"]
        if version:
            clone_cmd.extend(["--branch", version])
        clone_cmd.extend([url, str(target_dir)])

        version_str = f" at {version}" if version else " (latest)"
        print(f"[DazzleNodes] Cloning {submodule_name}{version_str}...")

        try:
            # Remove the empty directory first (git clone needs it gone)
            import shutil
            if target_dir.exists():
                shutil.rmtree(target_dir)

            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print(f"[DazzleNodes] [OK] Cloned {submodule_name}")
                success_count += 1
            else:
                print(f"[DazzleNodes] [WARN] Failed to clone {submodule_name}")
                if result.stderr:
                    for line in result.stderr.strip().split('\n'):
                        if line:
                            print(f"[DazzleNodes]   {line}")
                # Recreate the empty directory so it doesn't break other logic
                target_dir.mkdir(parents=True, exist_ok=True)
                fail_count += 1
        except subprocess.TimeoutExpired:
            print(f"[DazzleNodes] [WARN] Clone of {submodule_name} timed out")
            fail_count += 1
        except Exception as e:
            print(f"[DazzleNodes] [WARN] Clone of {submodule_name} failed: {e}")
            fail_count += 1

    if success_count > 0:
        print(f"[DazzleNodes] [OK] Cloned {success_count} submodule(s)")
    if fail_count > 0:
        print(f"[DazzleNodes] [WARN] {fail_count} submodule(s) failed to clone")

    return fail_count == 0


def _init_submodules_if_needed():
    """Initialize git submodules if directories exist but are empty.

    Skips symlinks/junctions (dev mode) and directories that already have content.

    Strategy:
    1. Try git submodule update (works for git clone installs)
    2. Re-check if dirs are still empty (catches silent failures)
    3. Fall back to direct git clone from .gitmodules + submodule_versions.json
       (works for tarball/registry installs without .git directory)
    """
    base_dir = Path(__file__).parent
    nodes_dir = base_dir / "nodes"
    if not nodes_dir.exists():
        return

    empty_submodules = _find_empty_submodule_dirs(nodes_dir)
    if not empty_submodules:
        return

    print(f"[DazzleNodes] Empty submodule directories detected: {', '.join(empty_submodules)}")

    # Step 1: Try standard git submodule update
    print("[DazzleNodes] Running git submodule update --init --recursive...")
    try:
        result = subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=base_dir
        )
        if result.returncode != 0:
            print(f"[DazzleNodes] [WARN] Submodule init exited with code {result.returncode}")
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line:
                        print(f"[DazzleNodes]   {line}")
    except subprocess.TimeoutExpired:
        print("[DazzleNodes] [WARN] Submodule init timed out after 120 seconds")
    except FileNotFoundError:
        print("[DazzleNodes] [WARN] git not found — will try direct clone fallback")
    except Exception as e:
        print(f"[DazzleNodes] [WARN] Submodule init failed: {e}")

    # Step 2: Re-check if directories are still empty
    still_empty = _find_empty_submodule_dirs(nodes_dir)
    if not still_empty:
        print("[DazzleNodes] [OK] Submodules initialized successfully")
        return

    # Step 3: Fallback — clone directly from .gitmodules URLs
    print(f"[DazzleNodes] Submodule update did not populate: {', '.join(still_empty)}")
    print("[DazzleNodes] Attempting direct clone fallback (registry/tarball install)...")
    _clone_submodules_fallback(base_dir, still_empty)

_init_submodules_if_needed()

# Run auto-sync before loading nodes
_sync_web_resources()

# Initialize aggregator dictionaries
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
_loaded_nodes = []
_failed_nodes = []

print("[DazzleNodes] Loading node collection...")

# Current directory
_current_dir = Path(__file__).parent
_nodes_dir = _current_dir / "nodes"

# Helper function to load a node module from directory with hyphens
def load_node_module(node_dir_name, display_name):
    """Load a node module from a directory (even with hyphens in name)"""
    node_path = _nodes_dir / node_dir_name

    # Check for DISABLED marker (set by dev_mode.py disable command)
    if (node_path / "DISABLED").exists():
        print(f"[DazzleNodes] {display_name} is DISABLED (skipping)")
        return 0

    init_file = node_path / "__init__.py"

    if not init_file.exists():
        raise FileNotFoundError(f"__init__.py not found in {node_path}")

    # Load the module using importlib
    spec = importlib.util.spec_from_file_location(
        node_dir_name.replace("-", "_"),  # Module name (replace hyphens)
        init_file
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # Extract NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS
    if hasattr(module, 'NODE_CLASS_MAPPINGS'):
        NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
    else:
        raise AttributeError(f"Module {node_dir_name} has no NODE_CLASS_MAPPINGS")

    if hasattr(module, 'NODE_DISPLAY_NAME_MAPPINGS'):
        NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

    return len(module.NODE_CLASS_MAPPINGS)

# ============================================================================
# Load Smart Resolution Calculator
# ============================================================================
try:
    num_nodes = load_node_module("smart-resolution-calc", "Smart Resolution Calculator")
    _loaded_nodes.append(f"Smart Resolution Calculator ({num_nodes} nodes)")
except Exception as e:
    _failed_nodes.append(("Smart Resolution Calculator", str(e)))
    print(f"[DazzleNodes] [WARN] Could not load Smart Resolution Calculator: {e}")

# ============================================================================
# Load Fit Mask to Image
# ============================================================================
try:
    num_nodes = load_node_module("fit-mask-to-image", "Fit Mask to Image")
    _loaded_nodes.append(f"Fit Mask to Image ({num_nodes} nodes)")
except Exception as e:
    _failed_nodes.append(("Fit Mask to Image", str(e)))
    print(f"[DazzleNodes] [WARN] Could not load Fit Mask to Image: {e}")

# ============================================================================
# Load Plasma Noise Generators
# ============================================================================
try:
    num_nodes = load_node_module("dazzle-comfy-plasma-fast", "Plasma Noise Generators")
    _loaded_nodes.append(f"Plasma Noise Generators ({num_nodes} nodes)")
except Exception as e:
    _failed_nodes.append(("Plasma Noise Generators", str(e)))
    print(f"[DazzleNodes] [WARN] Could not load Plasma Noise Generators: {e}")

# ============================================================================
# Load Preview Bridge Extended
# ============================================================================
try:
    num_nodes = load_node_module("preview-bridge-extended", "Preview Bridge Extended")
    _loaded_nodes.append(f"Preview Bridge Extended ({num_nodes} nodes)")
except Exception as e:
    _failed_nodes.append(("Preview Bridge Extended", str(e)))
    print(f"[DazzleNodes] [WARN] Could not load Preview Bridge Extended: {e}")

# ============================================================================
# Load Dazzle Switch
# ============================================================================
try:
    num_nodes = load_node_module("dazzle-switch", "Dazzle Switch")
    _loaded_nodes.append(f"Dazzle Switch ({num_nodes} nodes)")
except Exception as e:
    _failed_nodes.append(("Dazzle Switch", str(e)))
    print(f"[DazzleNodes] [WARN] Could not load Dazzle Switch: {e}")

# ============================================================================
# Report Loading Status
# ============================================================================
if _loaded_nodes:
    print(f"[DazzleNodes] [OK] Loaded {len(_loaded_nodes)} nodes: {', '.join(_loaded_nodes)}")
    print(f"[DazzleNodes] [OK] {len(NODE_CLASS_MAPPINGS)} node(s) available")

if _failed_nodes:
    print(f"[DazzleNodes] [WARN] Failed to load {len(_failed_nodes)} nodes:")
    for node_name, error in _failed_nodes:
        print(f"[DazzleNodes]    - {node_name}: {error}")

if not _loaded_nodes:
    print("[DazzleNodes] [FAIL] No nodes loaded! Check submodule initialization.")
    print("[DazzleNodes]    Run: git submodule update --init --recursive")

# Web directory for JavaScript widgets
WEB_DIRECTORY = "./web"

# Export for ComfyUI
__all__ = [
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
    'WEB_DIRECTORY',
    '__version__',
    'VERSION',
    'BASE_VERSION',
    'PIP_VERSION'
]
