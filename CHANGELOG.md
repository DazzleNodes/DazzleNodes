# Changelog

All notable changes to DazzleNodes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.1-alpha] - 2026-02-24

### Changed
- **Dazzle Switch** updated to [v0.4.0-alpha](https://github.com/DazzleNodes/ComfyUI-DazzleSwitch/releases/tag/v0.4.0-alpha)
  - Fallback modes: `priority` (rgthree-style), `strict` (no fallback), `sequential` (next slot with wrap-around)
  - `(none)` dropdown option: skip dropdown, let mode decide (6-behavior matrix)
  - Negative indexing: `select_override = -1` selects last connected, `-2` second-to-last, etc.
  - Widget dimming: `select_override` dims at 35% opacity when value is 0
  - Sequential mode gap fix: correctly scans through disconnected slot positions
  - 86 tests (31 new)
- **Web sync script** rewritten with per-node caching
  - Each node's web files hashed independently (`.sync_hashes.json`)
  - Symlinked nodes (dev mode) always sync; submodule nodes cache by content hash
  - Scales efficiently to large node collections (no global re-sync)

## [0.5.0-alpha] - 2026-02-23

### Added
- **Dazzle Switch** - New smart switch node with dropdown-based input selection
  - Added as submodule: [ComfyUI-DazzleSwitch](https://github.com/DazzleNodes/ComfyUI-DazzleSwitch) (v0.3.1-alpha)
  - Dynamic input expansion (auto-grow/shrink slots)
  - Type detection via graph walking with output type label
  - Slot reordering (right-click Move Up / Move Down) for cascading alignment
  - `selected_index` → `select_override` cascading across chained switches
  - Label cache preserves user renames across reconnect cycles
  - Active slot highlight for visual feedback

### Changed
- **Web sync script** - Fixed CWD-independent path resolution
  - Uses `Path(__file__).resolve().parent.parent` instead of relative paths
  - Sync now works correctly when called from any working directory

## [0.4.1-alpha] - 2025-01-27

### Added
- **LICENSE** - Added MIT license file
- **CONTRIBUTING.md** - Replaced stub with project-specific contribution guidelines

### Fixed
- **Auto-initialize submodules** on first startup when installed via ComfyUI Manager
  - Detects empty submodule directories and runs `git submodule update --init --recursive`
  - Skips symlinks/junctions (dev mode) to avoid clobbering local development setups
  - Skips directories that already have content
- **README** - Updated installation instructions to reflect published ComfyUI Registry status
- **CODEOWNERS** - Fixed GitHub username
- **Issue templates** - Fixed project name in bug report and feature request templates

## [0.4.0-alpha] - 2025-01-27

### Added
- **Preview Bridge Extended** - New node for extended preview bridge functionality
  - Added as submodule: [ComfyUI-PreviewBridgeExtended](https://github.com/DazzleNodes/ComfyUI-PreviewBridgeExtended)

### Changed
- **Smart Resolution Calculator Updated** - Updated to v0.6.6
  - Fixed crash when image mode disabled with no connected image (NoneType error)
  - Corrected image_mode default from enabled to disabled
  - Added safeguard for pending calculator states
  - See [Smart Resolution Calc v0.6.6 release](https://github.com/djdarcy/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.6.6) for full details

### Developer
- **dev_mode.py** - Added local path resolution support
  - New `dev_mode_local.yaml` config for developer-specific local paths (gitignored)
  - New `--local` flag for `dev` command to prefer local config
  - Added `dev_mode_local.yaml.example` template
- **Documentation** - Added `docs/` directory
  - `dynamic-node-loading.md` - Guide to the aggregator architecture and building your own node collection
  - `git-submodule-workaround.md` - Workaround for silent `git submodule add` failure on Windows

## [0.3.6-alpha] - 2025-11-24

### Fixed
- **Plasma Noise Generators** - Fixed OmniNoise execution failures (updated to v0.4.0 rebuild)
  - Fixed optional parameter handling when widgets are hidden by JavaScript
  - Fixed Plasma noise delegation (was calling wrong method name)
  - Added fallback error handling for unknown noise types
  - See [dazzle-comfy-plasma-fast v0.4.0 release](https://github.com/DazzleNodes/dazzle-comfy-plasma-fast/releases/tag/v0.4.0) for full details

## [0.3.5-alpha] - 2025-11-24

### Fixed
- **Plasma Noise Generators** - Fixed OmniNoise dynamic widget visibility not working when installed via DazzleNodes package
  - JS now uses dynamic imports with auto-depth detection for path compatibility
  - Works in both standalone and DazzleNodes installation modes

## [0.3.4-alpha] - 2025-11-24

### Changed
- **Plasma Noise Generators Updated** - Updated to v0.4.0
  - Added OmniNoise unified generator combining all 5 noise types
  - Dynamic widget visibility (turbulence for Plasma, distribution for Random)
  - Two random distributions: Uniform (TV Static) and Gaussian (Centered Gray)
  - Uniform distribution maintains 100% backwards compatibility with RandNoise node
  - JavaScript-based widget management for intelligent UI
  - See [dazzle-comfy-plasma-fast v0.4.0 release](https://github.com/DazzleNodes/dazzle-comfy-plasma-fast/releases/tag/v0.4.0) for full details

## [0.3.3-alpha] - 2025-11-15

### Changed
- **Fit Mask to Image Updated** - Updated to v0.2.3-alpha
  - Added `missing_mask` parameter for empty mask handling
  - Default changed to `pass_through` for better workflow compatibility
  - Four modes: pass_through (default), all_visible, all_hidden, error
  - Auto-generates masks when explicitly requested
  - Includes example workflows demonstrating all modes
  - See [Fit Mask to Image v0.2.3-alpha release](https://github.com/DazzleNodes/fit-mask-to-image/releases/tag/v0.2.3-alpha) for full details

## [0.3.1-alpha] - 2025-11-12

### Changed
- **Smart Resolution Calculator Updated** - Updated to v0.6.5
  - img2img workflow support with VAE encoding
  - Generator node compatibility (KSampler, RandomNoise)
  - Pending data display with `(?:?)` for unknown dimensions
  - SCALE tooltip UX improvements (stays visible while hovering, precise handle targeting)
  - Info output polish (removed duplication, added AR field, VAE encoding status)
  - Bug fixes for mutual exclusivity and reconnection handling
  - See [Smart Resolution Calc v0.6.5 release](https://github.com/djdarcy/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.6.5) for full details

## [0.3.0-alpha] - 2025-11-02

Initial alpha release with three nodes:
- Smart Resolution Calculator (v0.6.2)
- Fit Mask to Image
- Plasma Noise Generators (dazzle-comfy-plasma-fast fork)
