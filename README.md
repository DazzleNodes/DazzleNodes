# DazzleNodes

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ComfyUI Registry](https://img.shields.io/badge/ComfyUI-Registry-green.svg)](https://registry.comfy.org/publishers/djdarcy/nodes/comfyui-dazzlenodes)
[![GitHub release](https://img.shields.io/github/v/release/DazzleNodes/DazzleNodes?include_prereleases&label=version)](https://github.com/DazzleNodes/DazzleNodes/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A curated collection of image/latent creation and transformation custom nodes for ComfyUI. Each node is independently developed and maintained, but packaged together for convenient installation.

## Included Nodes

### Smart Resolution Calculator (standalone: **[Github](https://github.com/djdarcy/ComfyUI-Smart-Resolution-Calc) & [Comfy Registry](https://registry.comfy.org/publishers/djdarcy/nodes/comfyui-smart-resolution-calc)**)
Flexible resolution and latent generation with intelligent aspect ratio handling.

**Features:**
- Toggle-based dimension control
- Automatic missing value calculation
- Preview image generation
- Direct latent output for sampling
- Custom widgets for enhanced UX

**Status:** Published standalone in [ComfyUI Registry](https://registry.comfy.org/publishers/djdarcy/nodes/comfyui-smart-resolution-calc) and in [DazzleNodes package](https://registry.comfy.org/publishers/djdarcy/nodes/comfyui-dazzlenodes) in ComfyUI Registry

### Fit Mask to Image (standalone: **[Github](https://github.com/DazzleNodes/fit-mask-to-image)**)
Automatically resizes masks to match image dimensions for inpainting workflows (for when the ksampler output no longer matches the input mask)

**Features:**
- Replaces [10-node workflow](https://gist.github.com/djdarcy/5796b7b2d705278aa4ad612248fd7c77) with single node
- Automatic dimension matching
- Preview output for verification
- Latent masking support
- Nearest-exact scaling for quality preservation

**Status:** Available from [DazzleNodes package](https://registry.comfy.org/publishers/djdarcy/nodes/comfyui-dazzlenodes) in the Comfy Registry; download from [Github](https://github.com/DazzleNodes/fit-mask-to-image) to `ComfyUI\custom_nodes` for standalone install

## Installation

### Method 1: ComfyUI Manager (Recommended - Coming Soon)

Once published to ComfyUI Registry:
```
Search for "DazzleNodes" in ComfyUI Manager and click Install
```

### Method 2: Git Clone with Submodules

```bash
cd ComfyUI/custom_nodes
git clone --recursive https://github.com/DazzleNodes/DazzleNodes.git
```

**⚠️ Important:** The `--recursive` flag is required to download all node submodules!

### Method 3: Manual Submodule Setup

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/DazzleNodes/DazzleNodes.git
cd DazzleNodes
git submodule update --init --recursive
```

### Method 4: Symlink for Development

If you're developing DazzleNodes locally:

```bash
cd ComfyUI/custom_nodes
mklink /D DazzleNodes C:\code\DazzleNodes\local
```

## Usage

After installation, restart ComfyUI. All nodes will appear under the **DazzleNodes** category in the node menu.

### Example Workflows

See `examples/` directory for workflow JSON files demonstrating node usage.

## Updating

### Update All Nodes
```bash
cd ComfyUI/custom_nodes/DazzleNodes
git pull
git submodule update --remote
```

### Update Individual Node
```bash
cd ComfyUI/custom_nodes/DazzleNodes/nodes/smart-resolution-calc
git pull
```

## Architecture

DazzleNodes uses **git submodules** for local development to maintain clean, independent histories for each node:

```
DazzleNodes/local/
├── __init__.py              # Aggregator that imports all nodes
├── nodes/                   # Node submodules
│   ├── smart-resolution-calc/    # Submodule → separate git repo
│   └── fit-mask-to-image/        # Submodule → separate git repo
└── examples/                # Collection-level examples
```

**Why Submodules?**
- Each node maintains independent git history
- Nodes can be extracted to standalone repos later
- Version locking prevents unexpected breakage
- Supports selective node development

## Development

### Working on a Node

Each node is developed in its own repository:

- **Smart Resolution Calculator**: `C:\code\smart-resolution-calc-repo\local`
- **Fit Mask to Image**: `C:\code\ComfyUI-ImageMask-Fix\local`

```bash
# Navigate to node's repository
cd nodes/fit-mask-to-image

# Make changes and commit as usual
git add -A
git commit -m "Add new feature"
git push

# Update collection to use new version
cd ../..
git add nodes/fit-mask-to-image
git commit -m "Update fit-mask-to-image to latest"
git push
```

### Adding a New Node

1. Create node repository
2. Add as submodule: `git submodule add <repo-url> nodes/<node-name>`
3. Update `__init__.py` to import the new node
4. Test in ComfyUI
5. Commit changes

## Troubleshooting

### Nodes Not Loading

**Symptom:** ComfyUI says "No nodes loaded!" or specific nodes are missing.

**Solution:** Initialize submodules:
```bash
cd ComfyUI/custom_nodes/DazzleNodes
git submodule update --init --recursive
```

### Empty Node Directories

**Symptom:** `nodes/` subdirectories exist but are empty.

**Solution:** You cloned without `--recursive` flag. Run:
```bash
cd ComfyUI/custom_nodes/DazzleNodes
git submodule update --init --recursive
```

### Import Errors

**Symptom:** Python import errors in console.

**Solution:**
1. Verify submodules are initialized
2. Check each node's `__init__.py` exists
3. Restart ComfyUI completely
4. Check ComfyUI console for detailed error messages

## Contributing

Contributions welcome! Each node has its own repository and contribution guidelines. See individual node READMEs for details.

For collection-level issues (installation, documentation, architecture), open an issue in this repository.

Like the project?

[!["Buy Me A Coffee"](https://camo.githubusercontent.com/0b448aabee402aaf7b3b256ae471e7dc66bcf174fad7d6bb52b27138b2364e47/68747470733a2f2f7777772e6275796d6561636f666665652e636f6d2f6173736574732f696d672f637573746f6d5f696d616765732f6f72616e67655f696d672e706e67)](https://www.buymeacoffee.com/djdarcy)

## License

DazzleNodes, Copyright (C) 2025 Dustin Darcy

Collection-level code is licensed under the MIT license - see the [LICENSE](LICENSE) file for details. 

See individual node directories for specific licenses. 
