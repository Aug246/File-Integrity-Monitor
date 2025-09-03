#!/bin/bash

# Sample Shell Script
# This file will be monitored for changes

echo "File Integrity Monitor Demo Script"
echo "=================================="

# Check if FIM is running
if pgrep -f "fim start" > /dev/null; then
    echo "✓ FIM monitoring is active"
else
    echo "✗ FIM monitoring is not running"
fi

# Display system information
echo ""
echo "System Information:"
echo "OS: $(uname -s)"
echo "Kernel: $(uname -r)"
echo "Hostname: $(hostname)"
echo "Current time: $(date)"

# Check monitored directories
echo ""
echo "Monitored Directories:"
for dir in /etc /usr/local/bin /var/log; do
    if [ -d "$dir" ]; then
        echo "✓ $dir (exists)"
    else
        echo "✗ $dir (not found)"
    fi
done

echo ""
echo "Demo script completed successfully!"
