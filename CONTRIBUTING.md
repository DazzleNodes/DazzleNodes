# Contributing to DazzleNodes

Thank you for considering contributing to DazzleNodes!

## Project Structure

DazzleNodes is a collection of independent nodes packaged together. Each node lives in its own repository and is included here as a git submodule:

```
nodes/
├── smart-resolution-calc/       → github.com/djdarcy/ComfyUI-Smart-Resolution-Calc
├── fit-mask-to-image/           → github.com/DazzleNodes/fit-mask-to-image
├── dazzle-comfy-plasma-fast/    → github.com/DazzleNodes/dazzle-comfy-plasma-fast
└── preview-bridge-extended/     → github.com/DazzleNodes/ComfyUI-PreviewBridgeExtended
```

## Where to Contribute

### Node-specific issues or features
Open issues and PRs in the **individual node's repository**, not here. Each node has its own maintainer guidelines.

### Collection-level issues
Open issues here for:
- Installation problems
- Aggregator/loader bugs (`__init__.py`)
- Documentation improvements
- Requests to add new nodes to the collection

## Reporting Bugs

1. Check existing issues to avoid duplicates
2. Include your ComfyUI version and installation method (Manager, git clone, etc.)
3. Include the relevant console output or error messages
4. Describe what you expected vs. what happened

## Pull Requests

1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Test in ComfyUI to verify nodes still load correctly
5. Submit a pull request with a clear description of the change

**Note:** If your PR modifies a submodule pointer, explain why the submodule update is needed.

## Development Setup

See the [Developer Tools guide](docs/developer-tools.md) for setting up a local development environment with `dev_mode.py`.

## Support the Project

If you find DazzleNodes useful, you can also support development in other ways:

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/djdarcy)
