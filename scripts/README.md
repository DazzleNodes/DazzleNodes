# DazzleNodes Development Scripts

This directory contains development and maintenance scripts for DazzleNodes.

## dev_mode.py

Development mode toggle script for managing DazzleNodes development workflow.

### Purpose

Manages switching between two modes:

- **Dev Mode** (symlinks): Direct links to source repositories for rapid development
- **Publish Mode** (submodules): Git submodules for version control and distribution

### Why Two Modes?

**Dev Mode Benefits:**
- Changes in source repos immediately visible in ComfyUI
- No commit → pull cycle needed during development
- Faster iteration and testing
- Work directly in your node's repository

**Publish Mode Benefits:**
- Clean git history with submodule tracking
- Version locking to specific commits
- Proper distribution structure
- Ready for git commits and publishing

### Requirements

Install required Python packages:

```bash
cd C:\code\DazzleNodes\local\scripts
pip install -r requirements.txt
```

**Required packages:**
- `pyyaml>=6.0` - YAML configuration file parsing

**Important**: Always run the script with `python dev_mode.py`, not just `dev_mode.py` directly. This ensures the correct Python interpreter (with installed dependencies) is used.

### Commands

#### Status Command

Check current state of all nodes:

```bash
# Quick status (default)
python dev_mode.py status

# Detailed status with git information
python dev_mode.py status --complete
```

**Quick Mode Output:**
- Shows if node is in dev (symlink) or publish (submodule) mode
- Checks if node path exists
- Verifies source repository exists

**Complete Mode Output:**
- All quick mode information
- Current git branch
- Latest commit
- Uncommitted changes warning
- Git status for both submodule and source repository

#### Dev Command

Switch nodes to development mode (creates symlinks):

```bash
# Switch single node
python dev_mode.py dev smart-resolution-calc
python dev_mode.py dev fit-mask-to-image

# Switch all nodes
python dev_mode.py dev all
```

**What It Does:**
1. Backs up existing node directory to `nodes_bak/` (with timestamp)
2. Removes existing submodule directory
3. Creates symlink/junction to source repository
4. Verifies symlink creation

**After Running:**
- Changes in `C:\code\smart-resolution-calc-repo\local\` immediately visible in ComfyUI
- No git operations needed for testing
- Restart ComfyUI to see changes

#### Publish Command

Switch nodes to publish mode (restores submodules):

```bash
# Restore single node
python dev_mode.py publish smart-resolution-calc

# Restore all nodes
python dev_mode.py publish all
```

**What It Does:**
1. Backs up symlink info to `nodes_bak/`
2. Removes symlink
3. Restores git submodule with `git submodule update --init`
4. Submodule points to last committed version

**After Running:**
- Node directory is git submodule again
- Ready for git commit operations
- Changes in source repo NOT visible until committed and pulled

### Global Options

```bash
-v, --verbose       # Show detailed operation logs
--dry-run          # Preview changes without making them
--no-backup        # Skip backup creation (dangerous)
```

**Examples:**

```bash
# See what would happen without making changes
python dev_mode.py --dry-run dev all

# Verbose output for debugging
python dev_mode.py -v dev smart-resolution-calc

# Skip backup (not recommended)
python dev_mode.py --no-backup publish all
```

### Configuration

Edit `dev_mode_config.yaml` to set defaults:

```yaml
# Default status mode
status_default_mode: quick  # or "complete"

# Backup before operations
backup_enabled: true

# Verbose output
verbose: false
```

**Configuration Precedence:**
1. Command line flags (highest priority)
2. Environment variables
3. Config file
4. Hardcoded defaults (lowest priority)

**Environment Variables:**

```bash
# Set default status mode
export DEV_MODE_STATUS_DEFAULT=complete

# Enable verbose output
export DEV_MODE_VERBOSE=1
```

### Typical Development Workflow

#### Starting Development Work

```bash
# 1. Check current status
python dev_mode.py status

# 2. Switch to dev mode
python dev_mode.py dev all

# 3. Make changes in source repositories
cd C:\code\smart-resolution-calc-repo\local\py
# ... edit smart_resolution_calc.py ...

# 4. Restart ComfyUI to test changes
# Changes are immediately visible!

# 5. Iterate: edit → restart → test
```

#### Preparing to Commit

```bash
# 1. Commit changes in source repository
cd C:\code\smart-resolution-calc-repo\local
git add -A
git commit -m "Add new feature"

# 2. Switch back to publish mode
cd C:\code\DazzleNodes\local
python dev_mode.py publish all

# 3. Update submodule to latest commit
cd nodes/smart-resolution-calc
git pull

# 4. Commit submodule update in DazzleNodes
cd ../..
git add nodes/smart-resolution-calc
git commit -m "Update smart-resolution-calc to latest"
```

### Safety Features

**Automatic Backups:**
- All destructive operations create timestamped backups
- Backups stored in `nodes_bak/` directory
- Each backup includes timestamp: `smart-resolution-calc_20251102_143015`

**Backup Contents:**
- Real directories: Full copy of directory
- Symlinks: Text file with symlink target information

**Restore from Backup:**
```bash
# Manual restoration if needed
cd C:\code\DazzleNodes\local\nodes
rm -rf smart-resolution-calc
cp -r ../nodes_bak/smart-resolution-calc_20251102_143015 smart-resolution-calc
```

**Dry Run Mode:**
- Preview all operations before executing
- No files modified
- Shows exact commands that would run

### Windows Symlink Details

**Symlink Creation:**
1. First attempts `mklink /D` (directory symlink)
2. Falls back to `mklink /J` (junction) if symlink fails
3. Junctions don't require administrator privileges

**Checking Symlink Status:**
- Script uses `dir /AL` to detect symlinks/junctions
- Works with both symlink types
- Handles Windows-specific link behavior

### Troubleshooting

#### "Already in dev mode" but changes not visible

**Solution:** ComfyUI may be caching. Restart ComfyUI completely.

#### Symlink creation fails

**Possible causes:**
- Node directory already exists (script should backup first)
- Source repository not found at expected path
- Permissions issue (junctions should work without admin)

**Solution:**
```bash
# Check status
python dev_mode.py status --complete

# Try with verbose output
python dev_mode.py -v dev smart-resolution-calc
```

#### Git submodule restore fails

**Possible causes:**
- .gitmodules configuration issue
- Submodule URL not accessible
- Git error (see error output)

**Solution:**
```bash
# Manual submodule restore
cd C:\code\DazzleNodes\local
git submodule update --init --recursive

# Check submodule status
git submodule status
```

#### Changes not showing after switching modes

**Dev Mode → Publish Mode:**
- Changes must be committed in source repo first
- Then pulled in submodule
- This is expected behavior

**Publish Mode → Dev Mode:**
- Restart ComfyUI after switching
- Symlink should point directly to source

#### Windows Store Python Issues

**Symptom:** Running `dev_mode.py` directly fails with missing PyYAML, but `python dev_mode.py` works fine.

**Cause:** Windows file association points to Microsoft Store Python stub instead of your real Python installation.

**Solution 1: Fix File Association (Recommended)**

Run the provided batch script as Administrator:
```cmd
scripts\fix_python_association.cmd
```

This will:
- Set `.py` files to use `C:\Python312\python.exe`
- Show current and new associations

**Solution 2: Disable Windows Store Python Stubs**

1. Open **Windows Settings**
2. Go to **Apps > Apps & features > App execution aliases**
3. Turn **OFF** both `python.exe` and `python3.exe` toggles
4. This removes the WindowsApps stubs from PATH

**Solution 3: Always Use `python` Command (Workaround)**

Just prefix commands with `python`:
```bash
python scripts\dev_mode.py status
```

### Node Mappings

Node mappings are **automatically discovered** from `.gitmodules`. No manual configuration needed!

The script parses `.gitmodules` to find all nodes:
```ini
[submodule "nodes/smart-resolution-calc"]
    path = nodes/smart-resolution-calc
    url = /c/code/smart-resolution-calc-repo/local

[submodule "nodes/fit-mask-to-image"]
    path = nodes/fit-mask-to-image
    url = /c/code/ComfyUI-ImageMask-Fix/local
```

**To Add New Node:**

1. Add as git submodule: `git submodule add <url> nodes/<node-name>`
2. That's it! The script automatically discovers it
3. Run `python dev_mode.py status` to verify

### Example Session

```bash
# Check what mode nodes are in
$ python dev_mode.py status
======================================================================
DazzleNodes Status (quick mode)
======================================================================

📦 smart-resolution-calc
   ─────────────────────────────────────────────────────────────────
   Status: 📁 PUBLISH MODE (submodule)
   Path: C:\code\DazzleNodes\local\nodes\smart-resolution-calc
   Source: ✓ C:\code\smart-resolution-calc-repo\local

📦 fit-mask-to-image
   ─────────────────────────────────────────────────────────────────
   Status: 📁 PUBLISH MODE (submodule)
   Path: C:\code\DazzleNodes\local\nodes\fit-mask-to-image
   Source: ✓ C:\code\ComfyUI-ImageMask-Fix\local

======================================================================

# Switch to dev mode
$ python dev_mode.py dev all
======================================================================
Switching to DEV MODE
======================================================================

Processing: smart-resolution-calc
  Backing up smart-resolution-calc to nodes_bak\smart-resolution-calc_20251102_143530
  ✓ Backup created
  ✓ Switched to dev mode

Processing: fit-mask-to-image
  Backing up fit-mask-to-image to nodes_bak\fit-mask-to-image_20251102_143531
  ✓ Backup created
  ✓ Switched to dev mode

======================================================================
Result: 2/2 nodes switched to dev mode
======================================================================

# Verify
$ python dev_mode.py status
📦 smart-resolution-calc
   ─────────────────────────────────────────────────────────────────
   Status: 🔗 DEV MODE (symlink)
   Target: C:\code\smart-resolution-calc-repo\local
   Source: ✓ C:\code\smart-resolution-calc-repo\local

📦 fit-mask-to-image
   ─────────────────────────────────────────────────────────────────
   Status: 🔗 DEV MODE (symlink)
   Target: C:\code\ComfyUI-ImageMask-Fix\local
   Source: ✓ C:\code\ComfyUI-ImageMask-Fix\local
```

### Related Documentation

- [DazzleNodes README](../README.md) - Main project documentation
- [Architecture Plan](../private/claude/2025-11-02__01-36-45__node-dev-mode-toggle-script.md) - Design decisions
- [ComfyUI Custom Nodes](https://github.com/comfyanonymous/ComfyUI) - ComfyUI documentation

---

**Questions or Issues?**

Check the [DazzleNodes Architecture Plan](../private/claude/2025-11-02__01-36-45__node-dev-mode-toggle-script.md) for detailed design decisions and rationale.
