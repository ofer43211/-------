#!/bin/bash

# Interactive project runner
# Usage: ./tools/run-project.sh

set -e

echo "🚀 Unified Projects - Project Runner"
echo "====================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to list projects in a category
list_category() {
    local category=$1
    local path="packages/$category"

    if [ -d "$path" ]; then
        echo -e "${BLUE}$category projects:${NC}"
        local i=1
        for project in "$path"/*; do
            if [ -d "$project" ]; then
                echo "  $i. $(basename "$project")"
                ((i++))
            fi
        done
        echo ""
    fi
}

# Main menu
echo "Available categories:"
echo ""
echo "1. RoTEM Projects"
echo "2. Gemini Projects"
echo "3. AI Platforms"
echo "4. Tools"
echo "5. Infrastructure"
echo "6. List all projects"
echo "0. Exit"
echo ""

read -p "Select category (0-6): " category_choice

case $category_choice in
    1)
        CATEGORY="rotem"
        ;;
    2)
        CATEGORY="gemini"
        ;;
    3)
        CATEGORY="ai-platforms"
        ;;
    4)
        CATEGORY="tools"
        ;;
    5)
        CATEGORY="infrastructure"
        ;;
    6)
        echo ""
        list_category "rotem"
        list_category "gemini"
        list_category "ai-platforms"
        list_category "tools"
        list_category "infrastructure"
        exit 0
        ;;
    0)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# List projects in selected category
echo ""
list_category "$CATEGORY"

# Get list of projects
projects=()
for project in packages/$CATEGORY/*; do
    if [ -d "$project" ]; then
        projects+=("$(basename "$project")")
    fi
done

if [ ${#projects[@]} -eq 0 ]; then
    echo -e "${YELLOW}No projects found in this category yet.${NC}"
    echo "Run 'npm run consolidate' to clone projects."
    exit 0
fi

# Select project
read -p "Select project number: " project_choice

if [ "$project_choice" -lt 1 ] || [ "$project_choice" -gt ${#projects[@]} ]; then
    echo -e "${RED}Invalid project number${NC}"
    exit 1
fi

PROJECT=${projects[$((project_choice-1))]}
PROJECT_PATH="packages/$CATEGORY/$PROJECT"

echo ""
echo -e "${GREEN}Selected: $PROJECT${NC}"
echo "Path: $PROJECT_PATH"
echo ""

# Check if package.json exists
if [ ! -f "$PROJECT_PATH/package.json" ]; then
    echo -e "${YELLOW}No package.json found. This might not be a Node.js project.${NC}"
    read -p "Open in terminal anyway? (y/n): " open_anyway
    if [ "$open_anyway" != "y" ]; then
        exit 0
    fi
    cd "$PROJECT_PATH"
    exec $SHELL
fi

# Show available scripts
echo "Available commands:"
echo ""
if [ -f "$PROJECT_PATH/package.json" ]; then
    # Extract scripts from package.json
    scripts=$(cat "$PROJECT_PATH/package.json" | grep -A 100 '"scripts"' | grep '":' | head -20 | sed 's/.*"\(.*\)".*/\1/' | sed 's/:.*//')
    i=1
    declare -a script_array
    while IFS= read -r script; do
        echo "  $i. npm run $script"
        script_array+=("$script")
        ((i++))
    done <<< "$scripts"
fi

echo ""
echo "  0. Open terminal in project directory"
echo ""

read -p "Select command to run (0-$((i-1))): " command_choice

if [ "$command_choice" -eq 0 ]; then
    echo -e "${GREEN}Opening terminal in $PROJECT_PATH${NC}"
    cd "$PROJECT_PATH"
    exec $SHELL
elif [ "$command_choice" -gt 0 ] && [ "$command_choice" -lt $i ]; then
    SCRIPT=${script_array[$((command_choice-1))]}
    echo ""
    echo -e "${GREEN}Running: npm run $SCRIPT${NC}"
    echo ""
    cd "$PROJECT_PATH"
    npm install
    npm run "$SCRIPT"
else
    echo -e "${RED}Invalid command choice${NC}"
    exit 1
fi
