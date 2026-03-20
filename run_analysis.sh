#!/bin/bash
# Feature Evolution Analyzer - Bash Wrapper Script
# 
# Runs Python analyzer with proper environment setup.
# Usage: ./run_analysis.sh "repo_url" [output_dir]

set -e

REPO_URL="${1:-}"
OUTPUT_DIR="${2:-evolution_analysis}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if repo URL provided
if [ -z "$REPO_URL" ]; then
    log_error "Repository URL required"
    echo ""
    echo "Usage: $0 <repo_url> [output_dir]"
    echo ""
    echo "Supported URL Formats:"
    echo "  • https://github.com/owner/repo"
    echo "  • https://github.com/owner/repo.git"
    echo "  • git@github.com:owner/repo.git"
    echo "  • owner/repo (shorthand)"
    echo ""
    echo "Examples:"
    echo "  $0 'https://github.com/cucumber/cucumber-ruby'"
    echo "  $0 'cucumber/cucumber-ruby'"
    echo "  $0 'behave/behave' 'behave_analysis'"
    echo "  $0 'git@github.com:gherkin/gherkin.git'"
    echo ""
    echo "Popular Repositories:"
    echo "  • cucumber/cucumber-ruby"
    echo "  • behave/behave"
    echo "  • gherkin/gherkin"
    echo "  • cucumber/cucumber-jvm"
    exit 1
fi

log_info "Feature Evolution Analyzer"

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Using Python $PYTHON_VERSION"

# Check if requirements installed
if ! python3 -c "import git; import pandas; import matplotlib" 2>/dev/null; then
    log_warning "Required packages not found"
    log_info "Run: pip install -r requirements.txt"
    echo ""
    read -p "Install now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install -r requirements.txt
    else
        log_error "Cannot proceed without dependencies"
        exit 1
    fi
fi

log_success "Dependencies available"

# Run analysis
log_info "Starting analysis..."
log_info "Repository: $REPO_URL"
if [ "$OUTPUT_DIR" = "evolution_analysis" ]; then
    log_info "Output: Auto-generated (timestamp-based)"
    python3 feature_evolution_analyzer.py "$REPO_URL"
else
    log_info "Output: $OUTPUT_DIR"
    python3 feature_evolution_analyzer.py "$REPO_URL" --output-dir "$OUTPUT_DIR"
fi

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log_success "Analysis complete!"
    echo ""
    
    # Try to find the output directory if auto-generated
    if [ "$OUTPUT_DIR" = "evolution_analysis" ]; then
        # Find the most recently created evolution_analysis_* directory
        ACTUAL_DIR=$(ls -td evolution_analysis_*/ 2>/dev/null | head -1)
        if [ -z "$ACTUAL_DIR" ]; then
            ACTUAL_DIR="evolution_analysis/"
        fi
    else
        ACTUAL_DIR="$OUTPUT_DIR"
    fi
    
    log_info "Output files in: $ACTUAL_DIR"
    echo "  • ${ACTUAL_DIR}evolution_timeline.csv - Timeline"
    echo "  • ${ACTUAL_DIR}evolution_stats.json - Statistics"
    echo "  • ${ACTUAL_DIR}file_timeline.csv - File history"
    echo "  • ${ACTUAL_DIR}evolution_visualization.png - Visualization"
    echo ""
    
    # Try to open visualization on supported systems
    if command -v xdg-open &> /dev/null; then
        read -p "Open visualization? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            xdg-open "${ACTUAL_DIR}evolution_visualization.png"
        fi
    elif command -v open &> /dev/null; then
        read -p "Open visualization? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "${ACTUAL_DIR}evolution_visualization.png"
        fi
    fi
else
    log_error "Analysis failed (exit code: $EXIT_CODE)"
    exit $EXIT_CODE
fi
