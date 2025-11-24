# Changelog

All notable changes to DazzleNodes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
