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
        print(f"[DazzleNodes] Executing: {sys.executable} {sync_script} --verbose")
        result = subprocess.run(
            [sys.executable, str(sync_script), "--verbose"],  # Added --verbose for debugging
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
