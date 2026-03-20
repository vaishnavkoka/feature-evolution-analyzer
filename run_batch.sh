#!/bin/bash
# Feature Evolution Analyzer - Batch Analysis Wrapper
#
# Runs batch analysis with easy configuration
# Usage: ./run_batch.sh [output_dir]

set -e

OUTPUT_DIR="${1:-batch_analysis_results}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

log_info "Feature Evolution Analyzer - Batch Mode"

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Using Python $PYTHON_VERSION"

# Check dependencies
if ! python3 -c "import git; import pandas; import matplotlib" 2>/dev/null; then
    log_error "Required packages not found. Run: pip install -r requirements.txt"
    exit 1
fi

log_success "Dependencies available"
echo ""

# Show options
log_info "Batch Analysis Options:"
echo "  1. Default repositories (6 popular BDD projects)"
echo "  2. Custom repositories (specify on command line)"
echo "  3. From file (bdd_repositories.txt)"
echo "  4. Interactive (specify each repo)"
echo ""

read -p "Select option (1-4, default=1): " -n 1 -r choice
echo ""

case ${choice:-1} in
    1)
        log_info "Using default BDD repositories..."
        python3 batch_analysis.py --output-dir "$OUTPUT_DIR"
        ;;
    2)
        read -p "Enter repository URLs (space-separated): " repos
        python3 batch_analysis.py --repos $repos --output-dir "$OUTPUT_DIR"
        ;;
    3)
        if [ ! -f "bdd_repositories.txt" ]; then
            log_error "bdd_repositories.txt not found"
            exit 1
        fi
        log_info "Using repositories from bdd_repositories.txt..."
        python3 batch_analysis.py --repos-file bdd_repositories.txt --output-dir "$OUTPUT_DIR"
        ;;
    4)
        repos=""
        while true; do
            read -p "Enter repository (leave blank to start): " repo
            [ -z "$repo" ] && break
            repos="$repos $repo"
        done
        
        if [ -z "$repos" ]; then
            log_error "No repositories specified"
            exit 1
        fi
        
        python3 batch_analysis.py --repos $repos --output-dir "$OUTPUT_DIR"
        ;;
    *)
        log_error "Invalid option"
        exit 1
        ;;
esac

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    log_success "Batch analysis complete!"
    log_info "Results in: $OUTPUT_DIR"
    echo ""
    
    # Show comparison file if it exists
    COMPARISON=$(ls -t "$OUTPUT_DIR"/comparison_*.csv 2>/dev/null | head -1)
    if [ -f "$COMPARISON" ]; then
        log_info "Comparison results:"
        head -5 "$COMPARISON"
        echo "  ..."
    fi
else
    log_error "Batch analysis failed"
    exit $EXIT_CODE
fi
