#!/bin/bash

# File Integrity Monitor - Cleanup Script
# This script restores the repository to its original state after running the demo

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧹 Cleaning up FIM demo files...${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 1. Remove generated demo files
print_status "Removing demo database..."
rm -f demo_files/demo_fim.db

print_status "Removing demo exports..."
rm -f demo_files/demo_results.json
rm -f demo_files/demo_results.csv

print_status "Removing demo logs..."
rm -f demo_files/demo.log

# 2. Remove any FIM files from root directory
print_status "Removing root directory FIM files..."
rm -f fim.log
rm -f fim.db
rm -f fim.db-wal
rm -f fim.db-shm

# 3. Restore deleted demo files
print_status "Restoring deleted demo files..."

# Recreate temp.txt (deleted during demo)
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

# 4. Check for any other generated files
print_status "Checking for other generated files..."

# Look for any .db files that might have been created
find . -name "*.db" -type f 2>/dev/null | grep -v ".git" | while read file; do
    if [[ "$file" != "./demo_files/sample_files/"* ]]; then
        print_warning "Found database file: $file"
        read -p "Remove this file? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f "$file"
            print_status "Removed: $file"
        fi
    fi
done

# Look for any .log files that might have been created
find . -name "*.log" -type f 2>/dev/null | grep -v ".git" | while read file; do
    if [[ "$file" != "./demo_files/sample_files/logs/"* ]]; then
        print_warning "Found log file: $file"
        read -p "Remove this file? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f "$file"
            print_status "Removed: $file"
        fi
    fi
done

# 5. Verify cleanup
print_status "Verifying cleanup..."

# Check if demo files are restored
if [ -f "demo_files/sample_files/temp.txt" ]; then
    print_status "✓ temp.txt restored"
else
    print_warning "✗ temp.txt not found"
fi

# Check if generated files are removed
if [ ! -f "demo_files/demo_fim.db" ] && [ ! -f "demo_files/demo_results.json" ]; then
    print_status "✓ Demo files cleaned up"
else
    print_warning "✗ Some demo files still exist"
fi

# 6. Show repository status
print_status "Repository cleanup completed!"
echo ""
echo -e "${GREEN}Current repository state:${NC}"
echo "  - Demo files: restored"
echo "  - Generated databases: removed"
echo "  - Export files: removed"
echo "  - Log files: cleaned"
echo ""
echo -e "${GREEN}Ready for fresh demo runs!${NC}"
echo ""
echo "To run the demo again:"
echo "  cd demo_files"
echo "  ./demo_script.sh"
