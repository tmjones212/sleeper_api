#!/bin/bash

# Build script for Fantasy Football Website
# This script builds the website and handles common tasks

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
LEAGUE_ID="${LEAGUE_ID:-1181025001438806016}"
WEBSITE_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$WEBSITE_DIR/src"
DIST_DIR="$WEBSITE_DIR/dist"
BUILD_DIR="$WEBSITE_DIR/build"

echo -e "${BLUE}Fantasy Football Website Builder${NC}"
echo "================================"

# Function to check dependencies
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is required${NC}"
        exit 1
    fi
    
    # Check for required Python modules
    python3 -c "import sys; sys.path.append('$WEBSITE_DIR/../src')" 2>/dev/null || {
        echo -e "${RED}Error: Cannot find src directory${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✓ Dependencies OK${NC}"
}

# Function to build the site
build_site() {
    echo -e "${BLUE}Building website...${NC}"
    
    cd "$WEBSITE_DIR"
    python3 build/site_generator.py --build
    
    echo -e "${GREEN}✓ Build complete!${NC}"
    echo "  Output: $DIST_DIR/index.html"
}

# Function to update specific component
update_component() {
    local component=$1
    echo -e "${BLUE}Updating $component...${NC}"
    
    case $component in
        trades)
            python3 update_scripts/update_trades.py --league "$LEAGUE_ID"
            ;;
        network)
            python3 update_scripts/update_network.py --league "$LEAGUE_ID"
            ;;
        matchups)
            python3 update_scripts/update_matchups.py --league "$LEAGUE_ID"
            ;;
        *)
            echo -e "${RED}Unknown component: $component${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}✓ $component updated${NC}"
}

# Function to start dev server
start_dev_server() {
    echo -e "${BLUE}Starting development server...${NC}"
    echo "  URL: http://localhost:8000"
    echo "  Press Ctrl+C to stop"
    
    cd "$DIST_DIR"
    python3 -m http.server 8000
}

# Function to deploy
deploy() {
    echo -e "${BLUE}Deploying to production...${NC}"
    
    if [ ! -f "$DIST_DIR/index.html" ]; then
        echo -e "${RED}Error: No build found. Run './build.sh build' first${NC}"
        exit 1
    fi
    
    cp "$DIST_DIR/index.html" "$WEBSITE_DIR/../index.html"
    [ -f "$DIST_DIR/matchup_breakdowns.js" ] && cp "$DIST_DIR/matchup_breakdowns.js" "$WEBSITE_DIR/../"
    
    echo -e "${GREEN}✓ Deployed successfully${NC}"
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 [command] [options]

Commands:
    build           Build the complete website
    update [component]  Update specific component (trades, network, matchups)
    update-all      Update all dynamic components
    dev             Start development server
    deploy          Deploy to production
    clean           Remove generated files
    help            Show this help message

Options:
    --league ID     Set league ID (default: $LEAGUE_ID)

Examples:
    $0 build
    $0 update trades
    $0 update-all --league 123456789
    $0 dev
EOF
}

# Parse command line arguments
COMMAND=${1:-help}
shift || true

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --league)
            LEAGUE_ID="$2"
            shift 2
            ;;
        *)
            COMPONENT=$1
            shift
            ;;
    esac
done

# Execute command
case $COMMAND in
    build)
        check_dependencies
        build_site
        ;;
    update)
        check_dependencies
        if [ -z "$COMPONENT" ]; then
            echo -e "${RED}Error: Specify component to update (trades, network, matchups)${NC}"
            exit 1
        fi
        update_component "$COMPONENT"
        ;;
    update-all)
        check_dependencies
        update_component trades
        update_component network
        update_component matchups
        ;;
    dev)
        start_dev_server
        ;;
    deploy)
        deploy
        ;;
    clean)
        echo -e "${BLUE}Cleaning generated files...${NC}"
        rm -f "$DIST_DIR/index.html" "$DIST_DIR/matchup_breakdowns.js"
        echo -e "${GREEN}✓ Clean complete${NC}"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        usage
        exit 1
        ;;
esac