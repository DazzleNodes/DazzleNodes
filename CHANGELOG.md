# Changelog

All notable changes to DazzleNodes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
