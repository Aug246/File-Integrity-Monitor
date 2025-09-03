#!/bin/bash

# Simple File Integrity Monitor - Project Reset Script
# This script restores the project to its clean state after running demos or experiments

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Resetting Simple FIM project to clean state...${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if we're in the right directory
check_directory() {
    if [ ! -f "pyproject.toml" ] || [ ! -d "fim" ] || [ ! -d "demo_files" ]; then
        print_error "This doesn't appear to be the File-Integrity-Monitor project directory."
        print_error "Please run this script from the project root directory."
        exit 1
    fi
}

# Function to remove generated files
remove_generated_files() {
    print_status "Removing generated files..."
    
    # Remove database files
    rm -f fim.db fim.db-wal fim.db-shm
    rm -f demo_files/demo_fim.db demo_files/demo_fim.db-wal demo_files/demo_fim.db-shm
    
    # Remove log files
    rm -f fim.log
    rm -f demo_files/fim.log demo_files/demo.log
    
    # Remove export files
    rm -f demo_files/demo_results.json demo_files/demo_results.csv
    rm -f *.json *.csv 2>/dev/null || true
    
    # Remove Python build artifacts
    rm -rf *.egg-info/ 2>/dev/null || true
    rm -rf build/ dist/ 2>/dev/null || true
    
    # Remove Python cache
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove pytest cache
    rm -rf .pytest_cache/ 2>/dev/null || true
    
    print_status "Generated files removed"
}

# Function to restore demo files
restore_demo_files() {
    print_status "Restoring demo files..."
    
    # Restore temp.txt (deleted during demo)
    if [ ! -f "demo_files/sample_files/temp.txt" ]; then
        cat > demo_files/sample_files/temp.txt << 'EOF'
This is a temporary file that will be deleted during the demo.

The File Integrity Monitor will detect this deletion and log it as an event.

Temporary files like this are often excluded from monitoring in production environments
using patterns like "*.tmp" or "*.temp" in the exclude_patterns configuration.

This file demonstrates:
- File deletion detection
- Event logging
- Baseline comparison
- Change tracking
EOF
        print_status "Restored temp.txt"
    fi
    
    # Remove any new files that might have been created during demo
    if [ -f "demo_files/sample_files/newfile.txt" ]; then
        rm -f demo_files/sample_files/newfile.txt
        print_status "Removed newfile.txt"
    fi
    
    # Restore config.ini to original state if it was modified
    if [ -f "demo_files/sample_files/config.ini" ]; then
        cat > demo_files/sample_files/config.ini << 'EOF'
[Database]
host = localhost
port = 5432
name = myapp
user = admin

[Logging]
level = INFO
file = app.log
max_size = 10MB
EOF
        print_status "Restored config.ini to original state"
    fi
    
    print_status "Demo files restored"
}

# Function to verify clean state
verify_clean_state() {
    print_status "Verifying clean state..."
    
    # Check for any remaining generated files
    remaining_files=$(find . -name "*.db" -o -name "*.log" -o -name "*.json" -o -name "*.csv" 2>/dev/null | grep -v ".git" | grep -v "demo_files/sample_files/logs/" | grep -v "demo_files/sample_files/" || true)
    
    if [ -n "$remaining_files" ]; then
        print_warning "Some generated files still exist:"
        echo "$remaining_files"
    else
        print_status "✓ No generated files found"
    fi
    
    # Check if demo files are restored
    if [ -f "demo_files/sample_files/temp.txt" ]; then
        print_status "✓ temp.txt restored"
    else
        print_warning "✗ temp.txt not found"
    fi
    
    if [ -f "demo_files/sample_files/config.ini" ]; then
        print_status "✓ config.ini restored"
    else
        print_warning "✗ config.ini not found"
    fi
    
    # Check if FIM is still working
    if command -v fim >/dev/null 2>&1; then
        print_status "✓ FIM command available"
    else
        print_warning "✗ FIM command not found (may need to reinstall)"
    fi
}

# Function to show reset summary
show_reset_summary() {
    print_status "Project reset completed!"
    echo ""
    echo -e "${BLUE}Current project state:${NC}"
    echo "  - Generated databases: removed"
    echo "  - Log files: cleaned"
    echo "  - Export files: removed"
    echo "  - Python cache: cleared"
    echo "  - Demo files: restored"
    echo ""
    echo -e "${BLUE}Ready for:${NC}"
    echo "  - Fresh demo runs"
    echo "  - New experiments"
    echo "  - Clean testing"
    echo ""
    echo -e "${BLUE}To run the demo again:${NC}"
    echo "  cd demo_files"
    echo "  ./demo_script.sh"
    echo ""
    echo -e "${BLUE}To test the system:${NC}"
    echo "  fim version"
    echo "  fim init --path ./demo_files/sample_files"
}

# Main reset execution
main() {
    echo "Starting project reset at $(date)"
    echo ""
    
    # Check if we're in the right directory
    check_directory
    
    # Remove generated files
    remove_generated_files
    
    # Restore demo files
    restore_demo_files
    
    # Verify clean state
    verify_clean_state
    
    # Show summary
    show_reset_summary
}

# Run main function
main "$@"
