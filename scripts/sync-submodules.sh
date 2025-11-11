#!/bin/bash
# Sync all submodules to latest released versions
# Updates DazzleNodes version and stages changes
#
# Usage:
#   ./scripts/sync-submodules.sh [OPTIONS]
#
# Options:
#   --dry-run              Show what would be updated without making changes
#   --only <submodule>     Update only the specified submodule(s)
#
# Examples:
#   ./scripts/sync-submodules.sh
#   ./scripts/sync-submodules.sh --dry-run
#   ./scripts/sync-submodules.sh --only smart-resolution-calc
#   ./scripts/sync-submodules.sh --only smart-resolution-calc --only fit-mask-to-image

set -e  # Exit on error

# Parse arguments
DRY_RUN=false
ONLY_MODULES=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            echo "🔍 DRY RUN MODE - No changes will be made"
            echo ""
            shift
            ;;
        --only)
            if [[ -z "$2" || "$2" == --* ]]; then
                echo "Error: --only requires a submodule name"
                exit 1
            fi
            ONLY_MODULES+=("$2")
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Sync submodules to their latest released versions."
            echo "Automatically bumps DazzleNodes patch version and stages changes."
            echo ""
            echo "Options:"
            echo "  --dry-run              Preview changes without modifying anything"
            echo "  --only <submodule>     Update only the specified submodule(s)"
            echo "                         Can be specified multiple times"
            echo "  --help                 Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Update all submodules"
            echo "  $0 --dry-run                          # Preview all updates"
            echo "  $0 --only smart-resolution-calc       # Update only one submodule"
            echo "  $0 --only smart-resolution-calc \\"
            echo "     --only fit-mask-to-image           # Update multiple specific submodules"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get script and repo directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}DazzleNodes Submodule Sync${NC}"
echo "=========================================="
echo ""

# Check for uncommitted changes (skip in dry-run)
if [ "$DRY_RUN" = false ]; then
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "${RED}Error:${NC} DazzleNodes has uncommitted changes."
        echo "Please commit or stash your changes first."
        echo ""
        git status --short
        exit 1
    fi
fi

# Track if any submodules were updated
UPDATED_ANY=false
declare -a UPDATED_MODULES

# Temporary file for tracking updates
UPDATES_FILE="$REPO_ROOT/.submodule_updates.$$"
trap "rm -f '$UPDATES_FILE'" EXIT

# Show filtering info if --only was used
if [ ${#ONLY_MODULES[@]} -gt 0 ]; then
    echo "Filtering to only update: ${ONLY_MODULES[*]}"
    echo ""
fi

echo "Checking submodules for updates..."
echo ""

# Get list of submodules
SUBMODULES=$(git config --file .gitmodules --get-regexp path | awk '{print $2}')

for MODULE_PATH in $SUBMODULES; do
    if [ ! -d "$MODULE_PATH" ]; then
        echo -e "${YELLOW}Warning:${NC} Submodule $MODULE_PATH not found, skipping"
        continue
    fi

    MODULE_NAME=$(basename "$MODULE_PATH")

    # Check if we should process this module (if --only was specified)
    if [ ${#ONLY_MODULES[@]} -gt 0 ]; then
        SHOULD_PROCESS=false
        for FILTER in "${ONLY_MODULES[@]}"; do
            if [ "$MODULE_NAME" = "$FILTER" ]; then
                SHOULD_PROCESS=true
                break
            fi
        done

        if [ "$SHOULD_PROCESS" = false ]; then
            echo -e "${BLUE}[${MODULE_NAME}]${NC} Skipped (not in --only filter)"
            echo ""
            continue
        fi
    fi

    echo -e "${BLUE}[${MODULE_NAME}]${NC}"

    cd "$REPO_ROOT/$MODULE_PATH"

    # Fetch latest tags
    if ! git fetch --tags origin 2>/dev/null; then
        echo -e "  ${YELLOW}⚠${NC} Could not fetch tags, skipping"
        echo ""
        continue
    fi

    # Get current commit
    CURRENT=$(git rev-parse HEAD 2>/dev/null)
    CURRENT_SHORT=$(git rev-parse --short HEAD 2>/dev/null)

    # Try to describe current commit with a tag
    CURRENT_TAG=$(git describe --tags --exact-match HEAD 2>/dev/null || echo "")

    # Get latest tag from origin/main
    LATEST_TAG=$(git describe --tags --abbrev=0 origin/main 2>/dev/null || echo "")

    if [ -z "$LATEST_TAG" ]; then
        echo -e "  ${YELLOW}⚠${NC} No tags found, skipping"
        echo ""
        continue
    fi

    # Get commit of latest tag
    LATEST_COMMIT=$(git rev-parse "$LATEST_TAG^{commit}" 2>/dev/null)
    LATEST_SHORT=$(git rev-parse --short "$LATEST_TAG^{commit}" 2>/dev/null)

    # Check if update needed
    if [ "$CURRENT" != "$LATEST_COMMIT" ]; then
        if [ -n "$CURRENT_TAG" ]; then
            echo -e "  ${GREEN}↑${NC} Update available: ${CURRENT_TAG} → ${LATEST_TAG}"
        else
            echo -e "  ${GREEN}↑${NC} Update available: ${CURRENT_SHORT} → ${LATEST_TAG} (${LATEST_SHORT})"
        fi

        if [ "$DRY_RUN" = false ]; then
            git checkout "$LATEST_TAG" 2>/dev/null
            echo "UPDATED:$MODULE_NAME:$LATEST_TAG" >> "$UPDATES_FILE"
        fi

        UPDATED_ANY=true
    else
        if [ -n "$CURRENT_TAG" ]; then
            echo -e "  ${GREEN}✓${NC} Already at ${CURRENT_TAG}"
        else
            echo -e "  ${GREEN}✓${NC} Already at latest (${LATEST_TAG})"
        fi
    fi

    echo ""
done

cd "$REPO_ROOT"

# Check if any updates were made
if [ -f "$UPDATES_FILE" ]; then
    # Read updated modules
    while IFS=: read -r _ module tag; do
        UPDATED_MODULES+=("$module ($tag)")
    done < "$UPDATES_FILE"
fi

if [ "$UPDATED_ANY" = false ]; then
    echo -e "${GREEN}✓${NC} All submodules already at latest versions"
    echo ""
    exit 0
fi

if [ "$DRY_RUN" = true ]; then
    echo "=========================================="
    echo ""
    echo -e "${GREEN}Dry run complete.${NC}"
    echo ""
    echo "The following submodules would be updated:"
    for module in "${UPDATED_MODULES[@]}"; do
        echo "  • $module"
    done
    echo ""
    echo "Run without --dry-run to apply changes."
    exit 0
fi

# Bump DazzleNodes patch version
echo "=========================================="
echo ""
echo "Bumping DazzleNodes version..."
echo ""

# Read current version components
CURRENT_MAJOR=$(grep -E "^MAJOR = [0-9]+$" version.py | sed 's/.*= //')
CURRENT_MINOR=$(grep -E "^MINOR = [0-9]+$" version.py | sed 's/.*= //')
CURRENT_PATCH=$(grep -E "^PATCH = [0-9]+$" version.py | sed 's/.*= //')

# Increment patch version
NEW_PATCH=$((CURRENT_PATCH + 1))

echo "Version: $CURRENT_MAJOR.$CURRENT_MINOR.$CURRENT_PATCH → $CURRENT_MAJOR.$CURRENT_MINOR.$NEW_PATCH"

# Update version.py PATCH line
sed -i "s/^PATCH = $CURRENT_PATCH$/PATCH = $NEW_PATCH/" version.py

# Also update pyproject.toml if it exists
if [ -f "pyproject.toml" ]; then
    # Get phase from version.py
    PHASE=$(grep -E "^PHASE = " version.py | sed 's/.*= //' | sed 's/  *#.*//' | tr -d '"' | tr -d "'" | tr -d ' ' | grep -v "^None$" || echo "")

    if [ -n "$PHASE" ]; then
        NEW_VERSION="$CURRENT_MAJOR.$CURRENT_MINOR.$NEW_PATCH-$PHASE"
    else
        NEW_VERSION="$CURRENT_MAJOR.$CURRENT_MINOR.$NEW_PATCH"
    fi

    sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    echo "Updated pyproject.toml to $NEW_VERSION"
fi

# Run update-version.sh to update __version__ string
./scripts/update-version.sh --build

# Stage all changes
git add -A

# Create suggested commit message
SUGGESTED_MSG="Update submodules to latest versions

Updated submodules:"

for module in "${UPDATED_MODULES[@]}"; do
    SUGGESTED_MSG="$SUGGESTED_MSG
- $module"
done

SUGGESTED_MSG="$SUGGESTED_MSG

Bump DazzleNodes version for submodule updates"

# Show summary
echo ""
echo "=========================================="
echo ""
echo -e "${GREEN}✓${NC} Submodules synchronized and changes staged"
echo ""
echo "Updated modules:"
for module in "${UPDATED_MODULES[@]}"; do
    echo "  • $module"
done
echo ""
echo -e "${BLUE}Suggested commit message:${NC}"
echo "---"
echo "$SUGGESTED_MSG"
echo "---"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Review staged changes: git status"
echo "  2. Commit (use suggested message or customize):"
echo "     git commit -m \"Your message here\""
echo "  3. Push to GitHub: git push origin main"
echo ""
