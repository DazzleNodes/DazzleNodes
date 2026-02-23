"""
@author: djdarcy
@title: DazzleNodes
@nickname: DazzleNodes
@description: Collection of productivity custom nodes for ComfyUI workflows
"""

import sys
import importlib.util
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
def _init_submodules_if_needed():
    """Initialize git submodules if directories exist but are empty.

    Skips symlinks/junctions (dev mode) and directories that already have content.
    Only runs git submodule update for genuinely empty directories, which typically
    means the repo was cloned without --recursive.
    """
    nodes_dir = Path(__file__).parent / "nodes"
    if not nodes_dir.exists():
        return

    empty_submodules = []
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
        # Check if directory is empty (or only contains .git file)
        contents = list(child.iterdir())
        if len(contents) == 0 or (len(contents) == 1 and contents[0].name == ".git"):
            empty_submodules.append(child.name)

    if not empty_submodules:
        return

    print(f"[DazzleNodes] Empty submodule directories detected: {', '.join(empty_submodules)}")
    print("[DazzleNodes] Running git submodule update --init --recursive...")
    try:
        result = subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            print("[DazzleNodes] [OK] Submodules initialized successfully")
        else:
            print(f"[DazzleNodes] [WARN] Submodule init exited with code {result.returncode}")
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line:
                        print(f"[DazzleNodes]   {line}")
    except subprocess.TimeoutExpired:
        print("[DazzleNodes] [WARN] Submodule init timed out after 120 seconds")
    except FileNotFoundError:
        print("[DazzleNodes] [WARN] git not found — cannot auto-initialize submodules")
        print("[DazzleNodes]    Install git or run manually: git submodule update --init --recursive")
    except Exception as e:
        print(f"[DazzleNodes] [WARN] Submodule init failed: {e}")

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
