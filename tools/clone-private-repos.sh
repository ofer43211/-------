#!/bin/bash

# Script to clone private repositories through the local proxy
# Usage: ./clone-private-repos.sh

PROXY_PORT=$(git config --get remote.origin.url | grep -oP '127.0.0.1:\K[0-9]+')
BASE_URL="http://local_proxy@127.0.0.1:${PROXY_PORT}/git/ofer43211"

echo "🔐 Cloning Private Repositories"
echo "Using proxy: 127.0.0.1:${PROXY_PORT}"
echo ""

# Function to clone with retry
clone_repo() {
    local category=$1
    local repo_name=$2
    local org=${3:-ofer43211}

    local target_dir="packages/${category}/${repo_name}"

    if [ -d "$target_dir" ]; then
        echo "✓ ${repo_name} already exists, skipping"
        return 0
    fi

    echo "⤓ Cloning ${repo_name}..."

    local url="http://local_proxy@127.0.0.1:${PROXY_PORT}/git/${org}/${repo_name}"

    if git clone "$url" "$target_dir" 2>/dev/null; then
        echo "✅ Successfully cloned ${repo_name}"
        return 0
    else
        echo "❌ Failed to clone ${repo_name} (may need authorization)"
        return 1
    fi
}

# Track statistics
total=0
success=0
failed=0

# RoTEM Projects
echo "📦 RoTEM Projects"
for repo in rotem-group-chat RoTEM_Project rotem_system RoTEM_Dashboard rotem_brain RoTEM; do
    clone_repo "rotem" "$repo"
    total=$((total + 1))
    if [ $? -eq 0 ]; then success=$((success + 1)); else failed=$((failed + 1)); fi
done

echo ""
echo "📦 Gemini Projects"
# Try ReachingOut org first
clone_repo "gemini" "GeminiBiju_Unified" "ReachingOut"
total=$((total + 1))
if [ $? -eq 0 ]; then success=$((success + 1)); else failed=$((failed + 1)); fi

clone_repo "gemini" "gemini-biju"
total=$((total + 1))
if [ $? -eq 0 ]; then success=$((success + 1)); else failed=$((failed + 1)); fi

echo ""
echo "📦 AI Platforms"
for repo in btl-gpt-production-suite AI-Empire AIPROJ UltimateAgentConsole; do
    clone_repo "ai-platforms" "$repo"
    total=$((total + 1))
    if [ $? -eq 0 ]; then success=$((success + 1)); else failed=$((failed + 1)); fi
done

echo ""
echo "📦 Infrastructure"
clone_repo "infrastructure" "TheVortex_v4"
total=$((total + 1))
if [ $? -eq 0 ]; then success=$((success + 1)); else failed=$((failed + 1)); fi

echo ""
echo "================================"
echo "📊 Results:"
echo "  Total attempted: ${total}"
echo "  ✅ Succeeded: ${success}"
echo "  ❌ Failed: ${failed}"
echo "================================"

if [ $failed -gt 0 ]; then
    echo ""
    echo "⚠️  Some repositories require manual authorization."
    echo "Please contact the repository owner to grant access."
fi
