#!/bin/bash

# File Integrity Monitor Demo Script
# This script demonstrates the complete FIM workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLE_FILES_DIR="$DEMO_DIR/sample_files"
DB_PATH="$DEMO_DIR/demo_fim.db"
LOG_FILE="$DEMO_DIR/demo.log"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  File Integrity Monitor Demo${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if FIM is installed
check_fim_installation() {
    print_status "Checking FIM installation..."
    
    if command -v fim >/dev/null 2>&1; then
        print_status "FIM is installed and available"
        FIM_VERSION=$(fim version 2>/dev/null | grep -o 'v[0-9.]*' || echo "unknown")
        print_status "FIM Version: $FIM_VERSION"
    else
        print_error "FIM is not installed or not in PATH"
        print_status "Installing FIM from source..."
        
        # Try to install from source
        cd "$DEMO_DIR/.."
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
            pip install -e .
            print_status "FIM installed from source"
        else
            print_error "Cannot find requirements.txt. Please install FIM manually."
            exit 1
        fi
        cd "$DEMO_DIR"
    fi
}

# Function to create demo database
create_demo_database() {
    print_status "Creating demo database..."
    
    # Remove existing database if it exists
    if [ -f "$DB_PATH" ]; then
        rm "$DB_PATH"
        print_status "Removed existing demo database"
    fi
    
    # Create baseline for sample files
    print_status "Creating baseline for sample files..."
    fim init --path "$SAMPLE_FILES_DIR" --db "$DB_PATH" 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        print_status "Baseline created successfully"
    else
        print_error "Failed to create baseline"
        exit 1
    fi
}

# Function to demonstrate file changes
demonstrate_file_changes() {
    print_status "Demonstrating file change detection..."
    
    # Modify an existing file
    print_status "Modifying config.ini..."
    echo "# Modified at $(date)" >> "$SAMPLE_FILES_DIR/config.ini"
    
    # Create a new file
    print_status "Creating new file..."
    echo "This is a new file created during demo" > "$SAMPLE_FILES_DIR/newfile.txt"
    
    # Delete a file
    print_status "Deleting temp.txt..."
    rm -f "$SAMPLE_FILES_DIR/temp.txt"
    
    print_status "File changes completed"
}

# Function to verify changes
verify_changes() {
    print_status "Verifying file changes..."
    
    # Wait a moment for file system to settle
    sleep 2
    
    # Run verification
    fim verify --path "$SAMPLE_FILES_DIR" --db "$DB_PATH" 2>&1 | tee -a "$LOG_FILE"
    
    print_status "Verification completed"
}

# Function to check system status
check_status() {
    print_status "Checking system status..."
    
    fim status --db "$DB_PATH" 2>&1 | tee -a "$LOG_FILE"
    
    print_status "Status check completed"
}

# Function to export data
export_data() {
    print_status "Exporting database data..."
    
    # Export to JSON
    fim db-export --format json --output "$DEMO_DIR/demo_results.json" --db "$DB_PATH" 2>&1 | tee -a "$LOG_FILE"
    
    # Export to CSV
    fim db-export --format csv --output "$DEMO_DIR/demo_results.csv" --db "$DB_PATH" 2>&1 | tee -a "$LOG_FILE"
    
    print_status "Data export completed"
}

# Function to show demo results
show_results() {
    print_status "Demo Results Summary:"
    echo ""
    
    if [ -f "$DEMO_DIR/demo_results.json" ]; then
        echo -e "${BLUE}Generated Files:${NC}"
        echo "  - $DB_PATH (SQLite database)"
        echo "  - $DEMO_DIR/demo_results.json (JSON export)"
        echo "  - $DEMO_DIR/demo_results.csv (CSV export)"
        echo "  - $LOG_FILE (Demo log)"
        echo ""
        
        # Show some statistics from the JSON export
        if command -v jq >/dev/null 2>&1; then
            echo -e "${BLUE}Database Statistics:${NC}"
            BASELINE_COUNT=$(jq '.baseline_count' "$DEMO_DIR/demo_results.json" 2>/dev/null || echo "N/A")
            EVENTS_COUNT=$(jq '.events_count' "$DEMO_DIR/demo_results.json" 2>/dev/null || echo "N/A")
            echo "  - Baseline files: $BASELINE_COUNT"
            echo "  - Events recorded: $EVENTS_COUNT"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}What was demonstrated:${NC}"
    echo "  ✓ Baseline creation for file monitoring"
    echo "  ✓ File modification detection"
    echo "  ✓ File creation detection"
    echo "  ✓ File deletion detection"
    echo "  ✓ Database integrity verification"
    echo "  ✓ Data export in multiple formats"
    echo "  ✓ CLI interface usage"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  - Review the generated files"
    echo "  - Try running 'fim start' to begin real-time monitoring"
    echo "  - Modify files while monitoring is active"
    echo "  - Check the logs and database for events"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up demo environment..."
    
    # Stop any running FIM processes
    if pgrep -f "fim start" > /dev/null; then
        print_warning "Stopping running FIM processes..."
        pkill -f "fim start" || true
    fi
    
    print_status "Cleanup completed"
}

# Main demo execution
main() {
    echo "Starting FIM Demo at $(date)" > "$LOG_FILE"
    
    # Check if sample files directory exists
    if [ ! -d "$SAMPLE_FILES_DIR" ]; then
        print_error "Sample files directory not found: $SAMPLE_FILES_DIR"
        exit 1
    fi
    
    print_status "Demo directory: $DEMO_DIR"
    print_status "Sample files: $SAMPLE_FILES_DIR"
    print_status "Database: $DB_PATH"
    print_status "Log file: $LOG_FILE"
    echo ""
    
    # Run demo steps
    check_fim_installation
    create_demo_database
    demonstrate_file_changes
    verify_changes
    check_status
    export_data
    show_results
    
    echo ""
    print_status "Demo completed successfully!"
    print_status "Check the generated files and logs for details"
}

# Trap cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"
