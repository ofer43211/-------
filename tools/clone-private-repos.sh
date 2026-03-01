#!/bin/bash

# Script to clone private repositories through the local proxy
# Usage: ./clone-private-repos.sh

PROXY_PORT=$(git config --get remote.origin.url | grep -oP '127.0.0.1:\K[0-9]+')

if [ -z "$PROXY_PORT" ]; then
    echo "❌ Could not detect local proxy port from git remote origin URL."
    echo "   Make sure this repo was cloned through the local proxy."
    exit 1
fi

BASE_URL="http://local_proxy@127.0.0.1:${PROXY_PORT}/git"

echo "🔐 Cloning Private Repositories"
echo "Using proxy: 127.0.0.1:${PROXY_PORT}"
echo ""

# Track statistics
total=0
success=0
failed=0
failed_repos=""

# Function to clone with status tracking
clone_repo() {
    local category=$1
    local repo_name=$2
    local org=${3:-ofer43211}

    local target_dir="packages/${category}/${repo_name}"
    total=$((total + 1))

    if [ -d "$target_dir/.git" ]; then
        echo "  ✓ ${repo_name} already exists, skipping"
        success=$((success + 1))
        return 0
    fi

    # Remove leftover empty directory from a previous failed clone
    if [ -d "$target_dir" ]; then
        rm -rf "$target_dir"
    fi

    echo "  ⤓ Cloning ${repo_name}..."
    local url="${BASE_URL}/${org}/${repo_name}"

    if git clone "$url" "$target_dir" 2>/dev/null; then
        echo "  ✅ ${repo_name}"
        success=$((success + 1))
    else
        echo "  ❌ ${repo_name} (not authorized or does not exist)"
        failed=$((failed + 1))
        failed_repos="${failed_repos}\n  - ${category}/${repo_name}"
    fi
}

# RoTEM Projects
echo "📦 RoTEM Projects"
for repo in rotem-group-chat RoTEM_Project rotem_system RoTEM_Dashboard rotem_brain RoTEM; do
    clone_repo "rotem" "$repo"
done

echo ""
echo "📦 Gemini Projects"
clone_repo "gemini" "GeminiBiju_Unified" "ReachingOut"
clone_repo "gemini" "gemini-biju"

echo ""
echo "📦 AI Platforms"
for repo in btl-gpt-production-suite AI-Empire AIPROJ UltimateAgentConsole; do
    clone_repo "ai-platforms" "$repo"
done

echo ""
echo "📦 Infrastructure"
clone_repo "infrastructure" "TheVortex_v4"

echo ""
echo "================================"
echo "📊 Results:"
echo "  Total attempted: ${total}"
echo "  ✅ Succeeded: ${success}"
echo "  ❌ Failed: ${failed}"
echo "================================"

if [ $failed -gt 0 ]; then
    echo ""
    echo "⚠  Failed projects:"
    echo -e "$failed_repos"
    echo ""
    echo "These repositories may require additional authorization."
fi
