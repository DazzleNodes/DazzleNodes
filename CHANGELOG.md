# Changelog

All notable changes to DazzleNodes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.3-alpha] - 2026-03-30

### Changed
- **Smart Resolution Calculator** updated to [v0.11.4](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.11.4)
  - Per-node DazzleCommand state lookup via `_dazzle_dc_id` marker (#56, DazzleCommand#5)
  - Noodle-required orchestration — standalone nodes unaffected by unconnected DazzleCommands
  - `seed_intent='lock'` trusts JS-resolved seed (removed stale Python override)
- **Preview Bridge Extended** updated to [v0.4.3-alpha](https://github.com/DazzleNodes/ComfyUI-PreviewBridgeExtended/releases/tag/v0.4.3-alpha)
  - Deterministic preview filenames — fixes cache invalidation that re-executed downstream nodes
  - Per-node DazzleCommand state from signal dict (multi-DC support)
  - Repeat runs cached in 0.01s (vs 40s+ previously)
- **Dazzle Command** updated to [v0.2.4-alpha](https://github.com/DazzleNodes/ComfyUI-DazzleCommand/releases/tag/v0.2.4-alpha)
  - Per-node state registry (`DazzleCommandState` class) replaces global singleton
  - API keys state by node ID, JS deferred setState for correct ID assignment
  - Signal carries `active_state` (schema v2) for per-noodle PBE reading
- **Updated README** -- node descriptions, registry links, feature lists

## [0.6.2-alpha] - 2026-03-28

### Fixed
- **Registry publish**: Version bump to resolve ComfyUI Registry rejection of re-published
  v0.6.1-alpha. No code changes from v0.6.1-alpha.

## [0.6.1-alpha] - 2026-03-28

### Fixed
- **submodule_versions.json**: Updated to match actual submodule tags. ComfyUI Manager
  installs use this file (not git submodules) to resolve node versions. Missing update
  caused fresh installs to pull stale versions (PBE at v0.3.3 instead of v0.4.0-alpha).
- **dazzle-command**: Updated from v0.2.0-alpha to v0.2.1-alpha — fixes dynamic JS imports
  for DazzleNodes aggregate compatibility (play/pause buttons not appearing when loaded
  through DazzleNodes instead of standalone)

## [0.6.0-alpha] - 2026-03-28

### Added
- **dazzle-command**: New workflow orchestration node (v0.2.0-alpha)
  - Play/pause toggle coordinates seed control and execution gates
  - 5-mode seed control: one run then random, new seed each run, reuse last seed,
    keep widget value, SmartResCalc decides
  - Cache-transparent operation (83% time savings on play toggle)
  - Seed bar entry with priority over SmartResCalc widget
  - Debug logger with localStorage enable

### Changed
- **smart-resolution-calc**: Updated submodule from v0.10.6 to v0.11.0
  - DAZZLE_SIGNAL input for Dazzle Command orchestration
  - JS seed lock in prompt hook with 5-mode control
  - Prompt input stripping for cache-transparent noodle binding
  - Noise cache key split, seed random mode fix, SpectralBlend2D resize fix
  - Display name: "Smart Resolution Calculator (DazzleNodes)"
- **preview-bridge-extended**: Updated submodule from v0.3.5-alpha to v0.4.0-alpha
  - Preview Bridge Ext. Latent node (LATENT+VAE variant)
  - DAZZLE_SIGNAL input for play/pause gate control
  - node_base.py refactor for shared mask orchestration
- **dazzle-comfy-plasma-fast**: Updated submodule from v0.4.0 to v0.4.1
  - BlendImages: size_mode parameter (match A/B/larger/smaller/exact)

## [0.5.10-alpha] - 2026-03-22

### Changed
- **smart-resolution-calc**: Updated submodule from v0.10.4 to v0.10.6
  - Per-bin normalization (spectral whitening) — resolution-independent noise composition
  - DazzleOptionsNode — extensible advanced configuration (norm_mode, whitening, cutoff_curve)
  - feature_size parameter — decoupled from cutoff for resolution-independent workflows
  - Pixel cutoff mode, feature_size display, hover preview, axis tooltips
  - ColorPickerButton old-workflow guard, widget margin fixes, canvas state leak fix
  - Old behavior preserved via DazzleOptions `norm_mode: global_rms`
  - See [SmartResCalc v0.10.6 release notes](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.10.6) for details

## [0.5.9-alpha] - 2026-03-21

### Changed
- **smart-resolution-calc**: Updated submodule from v0.9.10 to v0.10.4
  - `image_purpose` widget with 5 modes (img2img, dimensions only, img2noise, image+noise, img2img+img2noise)
  - SpectralBlend2DWidget — 2D XY pad for blend_strength + cutoff visualization
  - Cutoff parameter exposed (was hardcoded at 0.2)
  - Preview thumbnail shows transformed input image
  - VAE-encode pattern source for artifact-free img2noise
  - Phase randomization for img2img+img2noise
  - IS_CHANGED caching fix for fixed seeds
  - Canvas corruption fix for older frontend versions
  - See [SmartResCalc v0.10.4 release notes](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.10.4) for details

### Fixed
- **dev_mode.py**: Handle read-only `.git/objects/pack` files on Windows during disable/publish

## [0.5.8-alpha] - 2026-03-19

### Fixed
- **__init__.py**: Submodule auto-init fallback for ComfyUI Registry installs
  - Registry distributes packages as tarballs without `.git` directory
  - `git submodule update --init --recursive` silently exits 0 but does nothing
  - New fallback: parses `.gitmodules` URLs and clones each submodule directly
  - Pinned versions via `submodule_versions.json` ensure correct tag is cloned

### Added
- **submodule_versions.json**: Manifest mapping submodule paths to pinned release tags
  - Must be updated alongside submodule pointer changes

## [0.5.7-alpha] - 2026-03-19

### Changed
- **smart-resolution-calc**: Updated submodule from v0.8.4 to v0.9.10
  - Full-stack modularization (JS: 5,379 -> 920 line orchestrator + 16 modules,
    Python: 2,296 -> 1,024 lines + 4 modules)
  - DazzleWidget/DazzleToggleWidget class hierarchy
  - Seed system rewrite (rgthree-style prompt interception)
  - Widget visibility correctness fix (splice -> draw override)
  - 122 automated tests (Vitest + Playwright + pytest)
  - See [SmartResCalc v0.9.10 release notes](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.9.10) for details

### Added
- **dev_mode.py**: `disable` and `enable` commands for temporarily disabling nodes during development
- **__init__.py**: DISABLED marker support — skips loading nodes marked with DISABLED file

### Release Note (will include unreleased v0.5.6-alpha)
- **dazzle-comfy-plasma-fast**: BlendImages fix described below

## [0.5.6-alpha] - 2026-03-14

### Fixed
- **dazzle-comfy-plasma-fast**: BlendImages resize result not assigned — PIL `Image.resize()` returns a new image but the result was silently discarded, so blending images of different sizes produced incorrect output

## [0.5.5-alpha] - 2026-03-14

### Changed
- **Smart Resolution Calculator** updated to [v0.8.4](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.8.4)
  - Fixed seed serialization — actual seed saved in workflow JSON for reproducibility
  - Persistent random mode with dice button toggle
  - Simplified from 106 to 62 lines using copy-return pattern
  - See [v0.8.4](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.8.4) release notes

## [0.5.4-alpha] - 2026-03-14

### Changed
- **Smart Resolution Calculator** updated to [v0.8.2](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.8.2)
  - Spectral blending — inject noise pattern spatial structure into latent for composition control
  - Seed widget with randomize/fix/recall buttons for reproducible noise generation
  - 5D video VAE support (Wan/Qwen/HunyuanVideo) — fixes crash on empty latent decode
  - Raw latent noise output with `use_as_noise` flag for sampler integration
  - `fill_type` always visible, `resolution` output replaced by `seed` INT output
  - See [v0.8.2](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.8.2) release notes

## [0.5.3-alpha] - 2026-03-06

### Changed
- **Smart Resolution Calculator** updated to [v0.7.0](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.7.0)
  - 5 new DazNoise fill types (Pink, Brown, Plasma, Greyscale, Gaussian) — auto-detected from dazzle-comfy-plasma-fast
  - New `fill_image` IMAGE input for custom fill from any source
  - Graceful fallback if dazzle-comfy-plasma-fast unavailable at execution time
  - See [v0.7.0](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.7.0) release notes

## [0.5.2-alpha] - 2026-03-01

### Changed
- **Smart Resolution Calculator** updated to [v0.6.8](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.6.8)
  - Fixed empty latent crash for non-SD1.5 VAEs (FLUX, patchified, Stable Cascade, Cosmos)
  - Latent now queries VAE for channel count and spatial compression ratio
  - Traffic analytics via ghtraf
  - See [v0.6.7](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.6.7) and [v0.6.8](https://github.com/DazzleNodes/ComfyUI-Smart-Resolution-Calc/releases/tag/v0.6.8) release notes

### Added
- **Traffic analytics** via [GitHub Traffic Tracker](https://github.com/djdarcy/github-traffic-tracker)
  - GitHub Actions workflow for daily traffic collection
  - Shields.io badges for installs and views
  - Static HTML dashboard at docs/stats/

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
