# Git Submodule Add: Silent Failure Workaround

## The Problem

When adding a new submodule to DazzleNodes using the standard `git submodule add` command, the operation can **silently fail** — exiting with code 0, producing no error output, and not actually adding the submodule.

```bash
# This silently does nothing:
git submodule add https://github.com/DazzleNodes/ComfyUI-PreviewBridgeExtended.git nodes/preview-bridge-extended
# Exit code: 0, no output, no submodule added
```

## When It Happens

This was observed with **Git 2.52.0 on Windows** (MSYS2/MinGW). The failure occurs when:

- The working tree has **any modified submodules** (staged or unstaged)
- Even a clean working tree with only untracked files may not be sufficient — the modified submodule pointer seems to be the trigger

The `git submodule` command is a shell script wrapper (`git-submodule.sh`) that delegates to the C built-in `git submodule--helper add`. The shell wrapper appears to lose or misroute the arguments on Windows under these conditions.

## Root Cause

The shell script at `<git-exec-path>/git-submodule` (line ~144) calls:

```bash
git ${wt_prefix:+-C "$wt_prefix"} submodule--helper add \
    $quiet $force $progress ... -- "$@"
```

When called through the wrapper, the helper exits in ~0.02 seconds without attempting to clone — indicating early bailout. However, calling the helper **directly** works fine:

```bash
# This works:
git submodule--helper add -- https://github.com/DazzleNodes/ComfyUI-PreviewBridgeExtended.git nodes/preview-bridge-extended
```

This suggests a path quoting or argument passing issue in the MSYS2 shell layer on Windows, possibly triggered by the `wt_prefix` variable or the state of the index.

## The Workaround

### Option A: Call submodule--helper directly

```bash
git submodule--helper add -- <url> <path>
```

This bypasses the shell wrapper and calls the C built-in directly. Note the `--` separator before the URL and path arguments.

### Option B: Commit first, then add

If the working tree has modified submodules, commit those changes first so the tree is clean, then run `git submodule add` normally.

```bash
# 1. Stage and commit the modified submodule
git add nodes/existing-submodule
git commit -m "Update existing-submodule to vX.Y.Z"

# 2. Now add the new submodule (may still silently fail on some Git versions)
git submodule add https://github.com/Example/NewNode.git nodes/new-node

# 3. If step 2 silently fails, use Option A instead
git submodule--helper add -- https://github.com/Example/NewNode.git nodes/new-node
```

### Option C: Use --force flag

Not tested in this case, but `git submodule add --force` may bypass some checks. Use with caution.

## How to Verify Success

After running the add command, check that all three of these are true:

```bash
# 1. Directory exists and has content
ls nodes/new-node/

# 2. .gitmodules has the new entry
cat .gitmodules | grep new-node

# 3. git status shows both .gitmodules and the new submodule staged
git status
# Should show:
#   modified:   .gitmodules
#   new file:   nodes/new-node
```

If any of these are missing, the add silently failed.

## Diagnostic Commands

When troubleshooting, these commands help identify the issue:

```bash
# Check for stale cached entries
git config --get submodule.nodes/new-node.url
git ls-files --stage -- nodes/new-node
ls .git/modules/nodes/

# Verify the remote is accessible
git ls-remote https://github.com/DazzleNodes/NewNode.git

# Run with tracing to see where it bails out
GIT_TRACE2=1 git submodule add <url> <path> 2>&1
# Look for: child_exit elapsed time < 0.1s = early bailout
```

## Future Resolution

This appears to be a Git-for-Windows issue with the `git-submodule` shell wrapper in specific conditions. Once resolved upstream, the standard `git submodule add` command should work as expected. Check the [Git for Windows release notes](https://github.com/git-for-windows/git/releases) for fixes related to submodule operations.

When a fix is available, the `submodule--helper` workaround can be retired in favor of the standard command.

## History

- **Discovered**: 2025-01-27
- **Git version**: 2.52.0.windows.1
- **Context**: Adding `ComfyUI-PreviewBridgeExtended` submodule to DazzleNodes
- **Confirmed working**: `git submodule--helper add --` (Option A)
