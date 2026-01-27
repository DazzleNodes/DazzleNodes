# Dynamic Node Loading Architecture

This document describes how DazzleNodes aggregates independently developed ComfyUI custom nodes into a single installable package using git submodules and dynamic module loading. This approach can serve as a template for anyone building their own multi-node ComfyUI collection.

## Overview

DazzleNodes solves a packaging problem: each custom node is developed in its own git repository with its own release cycle, but users want a single install. The solution has three layers:

1. **Git submodules** — each node lives in `nodes/<name>/` as an independent repo
2. **Dynamic module loading** — the root `__init__.py` discovers and imports each node at startup using `importlib`
3. **Web resource syncing** — JavaScript/CSS files from each submodule are synced to a unified `web/` directory for ComfyUI to serve

## Directory Structure

```
DazzleNodes/
├── __init__.py                  # Aggregator: loads all nodes dynamically
├── version.py                   # Collection version (auto-updated by hooks)
├── pyproject.toml               # ComfyUI Registry metadata
├── web/                         # Generated (gitignored) - synced JS/CSS
│   ├── core/                    # Shared libraries
│   ├── smart-resolution-calc/   # Synced from nodes/smart-resolution-calc/web/
│   └── ...
├── web_src/
│   └── core/                    # Shared JS libraries (e.g., dazzle_core.js)
├── nodes/                       # Git submodules
│   ├── smart-resolution-calc/   # Each is an independent git repo
│   ├── fit-mask-to-image/
│   ├── dazzle-comfy-plasma-fast/
│   └── preview-bridge-extended/
├── scripts/
│   ├── sync_web_files.py        # Web resource sync script
│   ├── dev_mode.py              # Dev/publish mode toggle
│   └── update-version.sh        # Version management
└── docs/                        # Documentation
```

## Layer 1: Submodule Contract

Each node submodule must expose a standard ComfyUI interface in its `__init__.py`:

```python
# Required: ComfyUI discovers nodes through these dictionaries
NODE_CLASS_MAPPINGS = {
    "MyNodeName": MyNodeClass,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MyNodeName": "My Node (Display Name)",
}
```

Beyond this, each submodule is free to organize its internals however it wants. Common patterns seen across DazzleNodes submodules:

```
nodes/my-node/
├── __init__.py          # Exports NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
├── py/                  # Python source (node logic)
│   ├── __init__.py      # May re-export mappings
│   └── my_node.py       # Node implementation
├── web/                 # JavaScript for custom widgets (optional)
│   └── my_node.js
├── version.py           # Node-level version tracking (optional)
└── pyproject.toml       # Standalone registry metadata (optional)
```

### Optional: WEB_DIRECTORY

If the node has JavaScript files (custom widgets, UI extensions), it should declare:

```python
WEB_DIRECTORY = "./web"
```

This tells ComfyUI where to find client-side code. The DazzleNodes sync system also reads from this location.

## Layer 2: Dynamic Module Loading

The root `__init__.py` uses `importlib` to load each submodule at startup. This is necessary because Python module names can't contain hyphens, but the submodule directories use them (e.g., `smart-resolution-calc`).

### The Loader

```python
import importlib.util
import sys
from pathlib import Path

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

_nodes_dir = Path(__file__).parent / "nodes"

def load_node_module(node_dir_name, display_name):
    """Load a node module from a directory (even with hyphens in name)."""
    node_path = _nodes_dir / node_dir_name
    init_file = node_path / "__init__.py"

    if not init_file.exists():
        raise FileNotFoundError(f"__init__.py not found in {node_path}")

    # Load using importlib — converts hyphens to underscores for module name
    spec = importlib.util.spec_from_file_location(
        node_dir_name.replace("-", "_"),
        init_file
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # Merge node mappings into the collection
    if hasattr(module, 'NODE_CLASS_MAPPINGS'):
        NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
    else:
        raise AttributeError(f"Module {node_dir_name} has no NODE_CLASS_MAPPINGS")

    if hasattr(module, 'NODE_DISPLAY_NAME_MAPPINGS'):
        NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

    return len(module.NODE_CLASS_MAPPINGS)
```

### Registering a Node

Each node is loaded with error isolation so one failing node doesn't break the collection:

```python
try:
    num_nodes = load_node_module("my-node-name", "My Node Display Name")
    _loaded_nodes.append(f"My Node ({num_nodes} nodes)")
except Exception as e:
    _failed_nodes.append(("My Node", str(e)))
    print(f"[DazzleNodes] [WARN] Could not load My Node: {e}")
```

### Why This Works

- `importlib.util.spec_from_file_location` loads a module from an arbitrary file path, bypassing Python's normal import resolution that chokes on hyphens
- Each submodule is registered in `sys.modules` so its internal relative imports work correctly
- The `NODE_CLASS_MAPPINGS` dictionaries are merged, so ComfyUI sees all nodes as coming from one package

## Layer 3: JavaScript — The Tricky Part

JavaScript is the most complex layer because ES6 import paths are **relative to the URL the script is served from**, and that URL changes depending on whether a node is installed standalone or as part of DazzleNodes.

### The Problem

When ComfyUI loads a custom node's JavaScript, the URL path depends on the installation:

| Mode | URL Path |
|------|----------|
| Standalone | `/extensions/smart-resolution-calc/smart_resolution_calc.js` |
| DazzleNodes | `/extensions/DazzleNodes/smart-resolution-calc/smart_resolution_calc.js` |

Static ES6 imports break because they assume a fixed nesting depth:

```javascript
// This works standalone (3 path segments):
import { app } from "../../scripts/app.js";
// /extensions/smart-resolution-calc/file.js → ../../ → /scripts/app.js ✓

// But fails inside DazzleNodes (4 path segments):
// /extensions/DazzleNodes/smart-resolution-calc/file.js → ../../ → /extensions/scripts/app.js ✗ (404)
```

### The Solution: Dynamic Import Depth Detection

DazzleNodes uses `import.meta.url` to calculate the correct path prefix at runtime. The core helper lives in `web_src/core/dazzle_core.js`:

```javascript
function calculateImportDepth() {
    const currentPath = import.meta.url;
    const urlParts = new URL(currentPath).pathname.split('/').filter(p => p);
    // Each part (including filename) requires one ../ to traverse up to root
    const depth = urlParts.length;
    return '../'.repeat(depth);
}
```

This works at any nesting depth:

| URL | Parts | Prefix | Resolves To |
|-----|-------|--------|-------------|
| `/extensions/my-node/file.js` | 3 | `../../../` | `/scripts/app.js` ✓ |
| `/extensions/DazzleNodes/my-node/file.js` | 4 | `../../../../` | `/scripts/app.js` ✓ |
| `/extensions/A/B/my-node/file.js` | 5 | `../../../../../` | `/scripts/app.js` ✓ |

### Implementation Pattern: Inline Helper

Each node that needs ComfyUI imports wraps its code in an async IIFE with a local depth calculator. This is the pattern used by `smart-resolution-calc` and `fit-mask-to-image`:

```javascript
// Dynamic import helper for standalone vs DazzleNodes compatibility
async function importComfyCore() {
    const currentPath = import.meta.url;
    const urlParts = new URL(currentPath).pathname.split('/').filter(p => p);
    const depth = urlParts.length;
    const prefix = '../'.repeat(depth);

    const [appModule, tooltipModule] = await Promise.all([
        import(`${prefix}scripts/app.js`),
        import('./tooltip_content.js')  // Local imports use relative paths
    ]);

    return {
        app: appModule.app,
        TOOLTIP_CONTENT: tooltipModule.TOOLTIP_CONTENT
    };
}

// Wrap entire extension in async IIFE
(async () => {
    const { app, TOOLTIP_CONTENT } = await importComfyCore();

    app.registerExtension({
        name: "MyNode.Extension",
        // ... extension code using app, ComfyWidgets, etc.
    });
})().catch(error => {
    console.error("[MyNode] Failed to load extension:", error);
});
```

### Implementation Pattern: Shared Core Library

For new nodes, `dazzle_core.js` exports helpers via `window.DazzleNodesCore`:

```javascript
// In your node's JavaScript:
(async () => {
    const { app, ComfyWidgets } = await window.DazzleNodesCore.importComfyCore();

    app.registerExtension({
        name: "MyNode.Extension",
        // ...
    });
})();
```

The shared library provides:
- `calculateImportDepth()` — returns the `../` prefix string
- `importComfyModules('app', 'widgets', ...)` — imports multiple ComfyUI modules
- `importComfyModule('app')` — imports a single module
- `importComfyCore()` — shortcut for `app` + `widgets`

### Standalone Compatibility

A common concern: does switching from static `import` statements to dynamic `import()` break the node when installed standalone (outside of DazzleNodes)?

**No.** The depth calculation is based entirely on the runtime URL, so the same code works in both contexts without any configuration or mode detection:

- **Standalone install** (`/extensions/my-node/file.js`): 3 segments → `../../../scripts/app.js` → `/scripts/app.js` ✓
- **DazzleNodes install** (`/extensions/DazzleNodes/my-node/file.js`): 4 segments → `../../../../scripts/app.js` → `/scripts/app.js` ✓

The node doesn't need to know which mode it's in. There's no flag, no environment variable, and no build step. The same `.js` file works identically in both scenarios.

The only behavioral difference is that dynamic `import()` is asynchronous (returns a Promise), which is why the entire extension must be wrapped in an async IIFE. This is a one-time structural change when adopting the pattern — after that, the node works everywhere.

### Gotcha: Depth Calculation Bug

An earlier version used `depth = urlParts.length - 2`, reasoning that the filename and root shouldn't count. This was wrong — every path segment (including the filename) requires one `../` to reach root. The correct formula is simply `depth = urlParts.length`.

### Web Resource Syncing

Since DazzleNodes aggregates multiple nodes, their JavaScript files need to be collected into one `web/` directory that ComfyUI can serve.

The `scripts/sync_web_files.py` script handles this automatically at startup (called from `__init__.py`):

1. **Shared libraries** from `web_src/core/` are synced first (highest priority)
2. **Submodule web files** from each `nodes/*/web/` are synced into `web/<node-name>/`
3. Files are **always copied** (ComfyUI's web server doesn't reliably follow symlinks)
4. An MD5 cache hash (`web/.sync_hash`) avoids unnecessary re-syncing on every startup
5. Sync uses an atomic temp-directory swap to prevent partial states

The `web/` directory is gitignored since it's generated at runtime.

File discovery is recursive (`rglob("**/*.js")`), so nodes can organize JavaScript in subdirectories (e.g., `web/managers/`, `web/utils/`) and the directory structure is preserved in the synced output.

## Building Your Own Node Collection

To create a similar multi-node package:

### 1. Create the collection repo

```bash
mkdir MyNodeCollection
cd MyNodeCollection
git init
```

### 2. Add nodes as submodules

```bash
git submodule add https://github.com/you/node-one.git nodes/node-one
git submodule add https://github.com/you/node-two.git nodes/node-two
```

> **Note:** See [git-submodule-workaround.md](git-submodule-workaround.md) if `git submodule add` silently fails.

### 3. Create the aggregator `__init__.py`

Use the `load_node_module` pattern shown above. Key points:
- Replace hyphens with underscores in module names
- Wrap each load in try/except for fault isolation
- Merge `NODE_CLASS_MAPPINGS` from each submodule into the collection's dict
- Report load status so users can diagnose issues

### 4. Ensure each node exports the contract

Each submodule's `__init__.py` must export `NODE_CLASS_MAPPINGS` (required) and `NODE_DISPLAY_NAME_MAPPINGS` (recommended).

### 5. Handle JavaScript (if applicable)

If any nodes have custom widgets or UI, you need to solve two problems:

**Problem 1: Collecting JS files from multiple submodules into one `web/` directory.**

Set `WEB_DIRECTORY = "./web"` in the root `__init__.py`, then either:
- Copy DazzleNodes' `sync_web_files.py` approach (auto-syncs `nodes/*/web/` → `web/*/` at startup)
- Or manually maintain a `web/` directory

**Problem 2: ES6 import paths break at different URL depths.**

Each node's JavaScript must use **dynamic imports with depth detection** instead of static `import` statements. Without this, a node that works standalone will produce 404 errors when loaded inside your collection (or vice versa). See [Layer 3: JavaScript](#layer-3-javascript--the-tricky-part) above for the full pattern.

The inline helper approach (async IIFE with `import.meta.url` depth calculation) is recommended because it makes each node self-contained — it works regardless of how the node is installed.

### 6. Register with ComfyUI Registry

Add a `pyproject.toml` with `[tool.comfy]` section for the ComfyUI Registry:

```toml
[project]
name = "my-node-collection"
version = "1.0.0"

[tool.comfy]
PublisherId = "your-id"
DisplayName = "My Node Collection"
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Git submodules over monorepo | Each node has independent history, releases, and can be installed standalone |
| `importlib` over standard imports | Python can't import from directories with hyphens; `importlib` bypasses this |
| Fault-isolated loading | One broken node shouldn't prevent the others from loading |
| Web sync at startup | Avoids committing generated files; adapts to dev/prod mode automatically |
| Dynamic JS imports via `import.meta.url` | Static ES6 imports break at different URL depths; runtime detection works everywhere |
| Always copy (never symlink) web files | ComfyUI's web server doesn't reliably follow symlinks |
| Merged NODE_CLASS_MAPPINGS | ComfyUI sees one flat namespace — no nesting required |

## Limitations

- **Namespace collisions**: If two submodules define the same node class name, the last one loaded wins. Use unique prefixes.
- **Startup cost**: Each submodule is imported at ComfyUI startup. Keep `__init__.py` lightweight.
- **Submodule complexity**: Git submodules have a learning curve. The `dev_mode.py` script helps by toggling between symlinks (dev) and submodules (publish).
