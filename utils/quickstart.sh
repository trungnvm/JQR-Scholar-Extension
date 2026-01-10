#!/bin/bash
#
# Quick Reference: Natural Sciences Data Collection
#
# This script provides quick commands for common tasks.
# Make it executable: chmod +x quickstart.sh
#

set -e  # Exit on error

UTILS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$UTILS_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Natural Sciences Data Collection${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to show usage
show_usage() {
    echo "Usage: ./quickstart.sh [command]"
    echo ""
    echo "Commands:"
    echo "  test        - Run quick test collection (50 journals per field)"
    echo "  demo        - Demonstrate module functionality"
    echo "  collect     - Run full data collection (requires email)"
    echo "  convert     - Convert CSV to JavaScript format"
    echo "  full        - Run complete pipeline (collect + convert)"
    echo "  verify      - Verify installation and modules"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./quickstart.sh test"
    echo "  ./quickstart.sh collect --email your@email.com"
    echo "  ./quickstart.sh full --email your@email.com --sjr-csv ../data/raw/scimagojr.csv"
}

# Parse command
COMMAND="${1:-help}"

case "$COMMAND" in
    test)
        echo -e "${GREEN}Running quick test collection...${NC}"
        echo ""
        python3 example_natural_sciences_collection.py --mode test
        ;;

    demo)
        echo -e "${GREEN}Running module demonstration...${NC}"
        echo ""
        python3 example_natural_sciences_collection.py --mode demo
        ;;

    collect)
        echo -e "${GREEN}Running full data collection...${NC}"
        echo ""
        shift  # Remove 'collect' from arguments

        if [ $# -eq 0 ]; then
            echo -e "${YELLOW}Warning: No email provided. API rate limits will be slower.${NC}"
            echo "Recommended: ./quickstart.sh collect --email your@email.com"
            echo ""
        fi

        python3 collect_natural_sciences_data.py "$@"
        ;;

    convert)
        echo -e "${GREEN}Converting CSV to JavaScript...${NC}"
        echo ""
        shift  # Remove 'convert' from arguments
        python3 convert_to_js.py "$@"
        ;;

    full)
        echo -e "${GREEN}Running complete pipeline...${NC}"
        echo ""
        shift  # Remove 'full' from arguments

        if [ $# -eq 0 ]; then
            echo -e "${YELLOW}Warning: No arguments provided.${NC}"
            echo "Recommended: ./quickstart.sh full --email your@email.com --sjr-csv ../data/raw/scimagojr.csv"
            echo ""
        fi

        echo -e "${BLUE}Step 1: Collecting data...${NC}"
        python3 collect_natural_sciences_data.py "$@"

        echo ""
        echo -e "${BLUE}Step 2: Converting to JavaScript...${NC}"
        python3 convert_to_js.py

        echo ""
        echo -e "${GREEN}✓ Complete pipeline finished!${NC}"
        ;;

    verify)
        echo -e "${GREEN}Verifying installation...${NC}"
        echo ""

        # Check Python version
        echo "Checking Python version..."
        python3 --version

        echo ""
        echo "Checking required modules..."
        python3 -c "
import sys
modules = ['pandas', 'requests', 'urllib3']
missing = []

for module in modules:
    try:
        __import__(module)
        print(f'✓ {module}')
    except ImportError:
        print(f'✗ {module} - NOT FOUND')
        missing.append(module)

if missing:
    print(f'\nMissing modules: {', '.join(missing)}')
    print('Install with: pip install -r requirements.txt')
    sys.exit(1)
else:
    print('\n✓ All required modules installed')
"

        echo ""
        echo "Checking project modules..."
        python3 -c "
import sys
from pathlib import Path

modules = [
    'journalListAggregator',
    'fieldClassifier',
    'impactFactorCollector',
    'collect_natural_sciences_data',
    'convert_to_js'
]

for module in modules:
    try:
        __import__(module)
        print(f'✓ {module}')
    except ImportError as e:
        print(f'✗ {module} - ERROR: {e}')
        sys.exit(1)

print('\n✓ All project modules loaded successfully')
"

        echo ""
        echo "Checking directories..."

        DIRS=(
            "../data/processed"
            "../data/fields/natural_sciences"
            "../data/raw"
        )

        for dir in "${DIRS[@]}"; do
            if [ -d "$dir" ]; then
                echo "✓ $dir"
            else
                echo "✗ $dir - NOT FOUND (will be created when needed)"
            fi
        done

        echo ""
        echo -e "${GREEN}✓ Verification complete!${NC}"
        ;;

    help|--help|-h)
        show_usage
        ;;

    *)
        echo -e "${YELLOW}Unknown command: $COMMAND${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac

exit 0
