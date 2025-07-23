#!/bin/bash

# PyPI Upload Script Wrapper for agno_cli
# This script provides a convenient way to upload the package to PyPI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --test          Upload to TestPyPI instead of PyPI"
    echo "  --dry-run       Show what would be done without doing it"
    echo "  --major         Bump major version (x.0.0)"
    echo "  --minor         Bump minor version (0.x.0)"
    echo "  --patch         Bump patch version (0.0.x) - default"
    echo "  --skip-tests    Skip running tests before upload"
    echo "  --force         Continue even if tests fail"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Upload with patch version bump"
    echo "  $0 --test --minor     # Upload to TestPyPI with minor version bump"
    echo "  $0 --dry-run          # Show what would be done"
    echo "  $0 --help             # Show this help"
}

# Parse command line arguments
PYTHON_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_usage
            exit 0
            ;;
        --test|--test-pypi)
            PYTHON_ARGS+=("--test")
            shift
            ;;
        --dry-run)
            PYTHON_ARGS+=("--dry-run")
            shift
            ;;
        --major)
            PYTHON_ARGS+=("--major")
            shift
            ;;
        --minor)
            PYTHON_ARGS+=("--minor")
            shift
            ;;
        --patch)
            PYTHON_ARGS+=("--patch")
            shift
            ;;
        --skip-tests)
            PYTHON_ARGS+=("--skip-tests")
            shift
            ;;
        --force)
            PYTHON_ARGS+=("--force")
            shift
            ;;
        *)
            print_colored $RED "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if we're in the right directory
if [[ ! -f "upload_to_pypi.py" ]]; then
    print_colored $RED "Error: upload_to_pypi.py not found in current directory"
    print_colored $YELLOW "Please run this script from the project root directory"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    print_colored $RED "Error: Python is not installed or not in PATH"
    exit 1
fi

# Run the Python script
print_colored $BLUE "Running PyPI upload script..."
python upload_to_pypi.py "${PYTHON_ARGS[@]}"

# Check exit status
if [[ $? -eq 0 ]]; then
    print_colored $GREEN "Upload script completed successfully!"
else
    print_colored $RED "Upload script failed!"
    exit 1
fi 