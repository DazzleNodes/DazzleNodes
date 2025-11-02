"""
@author: djdarcy
@title: DazzleNodes
@nickname: DazzleNodes
@description: Collection of productivity custom nodes for ComfyUI workflows
"""

import sys
from pathlib import Path

# Add nodes directory to Python path for imports
_current_dir = Path(__file__).parent
_nodes_dir = _current_dir / "nodes"

if str(_nodes_dir) not in sys.path:
    sys.path.insert(0, str(_nodes_dir))

# Initialize aggregator dictionaries
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
_loaded_nodes = []
_failed_nodes = []

print("[DazzleNodes] Loading node collection...")

# ============================================================================
# Load Smart Resolution Calculator
# ============================================================================
try:
    from smart_resolution_calc import (
        NODE_CLASS_MAPPINGS as SRC_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS as SRC_DISPLAY,
    )
    NODE_CLASS_MAPPINGS.update(SRC_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(SRC_DISPLAY)
    _loaded_nodes.append("Smart Resolution Calculator")
except Exception as e:
    _failed_nodes.append(("Smart Resolution Calculator", str(e)))
    print(f"[DazzleNodes] ⚠️  Could not load Smart Resolution Calculator: {e}")

# ============================================================================
# Load Fit Mask to Image
# ============================================================================
try:
    from fit_mask_to_image import (
        NODE_CLASS_MAPPINGS as FMI_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS as FMI_DISPLAY,
    )
    NODE_CLASS_MAPPINGS.update(FMI_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(FMI_DISPLAY)
    _loaded_nodes.append("Fit Mask to Image")
except Exception as e:
    _failed_nodes.append(("Fit Mask to Image", str(e)))
    print(f"[DazzleNodes] ⚠️  Could not load Fit Mask to Image: {e}")

# ============================================================================
# Report Loading Status
# ============================================================================
if _loaded_nodes:
    print(f"[DazzleNodes] ✓ Loaded {len(_loaded_nodes)} nodes: {', '.join(_loaded_nodes)}")
    print(f"[DazzleNodes] ✓ {len(NODE_CLASS_MAPPINGS)} node(s) available")

if _failed_nodes:
    print(f"[DazzleNodes] ⚠️  Failed to load {len(_failed_nodes)} nodes:")
    for node_name, error in _failed_nodes:
        print(f"[DazzleNodes]    - {node_name}: {error}")

if not _loaded_nodes:
    print("[DazzleNodes] ❌ No nodes loaded! Check submodule initialization.")
    print("[DazzleNodes]    Run: git submodule update --init --recursive")

# Web directory for JavaScript widgets
WEB_DIRECTORY = "./web"

# Export for ComfyUI
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
