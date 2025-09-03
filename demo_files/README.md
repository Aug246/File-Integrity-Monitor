# Demo Files for File Integrity Monitor

This directory contains sample files and a recorded run to demonstrate the FIM system capabilities.

## Contents

- `sample_files/` - Directory with sample files for testing
- `recorded_run/` - Sample database and logs from a monitoring session
- `demo_script.sh` - Automated demo script

## Quick Demo

1. **Create baseline:**
   ```bash
   fim init --path ./demo_files/sample_files
   ```

2. **Start monitoring:**
   ```bash
   fim start --config fim.yml --foreground
   ```

3. **In another terminal, make changes:**
   ```bash
   # Modify a file
   echo "Modified content" > demo_files/sample_files/config.ini
   
   # Create a new file
   echo "New file" > demo_files/sample_files/newfile.txt
   
   # Delete a file
   rm demo_files/sample_files/temp.txt
   ```

4. **Verify changes:**
   ```bash
   fim verify --path ./demo_files/sample_files
   ```

5. **Check status:**
   ```bash
   fim status
   ```

6. **Export data:**
   ```bash
   fim db-export --format json --output demo_results.json
   ```

## Sample Files Structure

```
sample_files/
├── config.ini          # Configuration file
├── script.sh           # Executable script
├── data.txt            # Data file
├── temp.txt            # Temporary file (will be deleted)
└── logs/
    ├── app.log         # Application log
    └── error.log       # Error log
```

## Expected Results

After running the demo, you should see:
- Baseline with 6 files
- Events for file modifications, creation, and deletion
- Database integrity verification
- Exportable results in JSON/CSV format

## Notes

- The demo uses a local SQLite database (`demo_fim.db`)
- All file operations are logged to `fim.log`
- The system detects changes in real-time when monitoring is active
- Use `Ctrl+C` to stop monitoring in foreground mode
