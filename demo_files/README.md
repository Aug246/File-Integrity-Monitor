# Demo Files for Simple File Integrity Monitor

This directory contains sample files and a demo script to help you learn how the FIM system works.

## 🎯 **What You'll Learn**

This demo will show you:
- How to create a baseline (snapshot) of files
- How to detect when files change
- How to verify file integrity
- How to export results

## 🚀 **Quick Demo (Step by Step)**

### **Step 1: Run the Demo Script**
```bash
# Make sure you're in the project root directory
cd /path/to/File-Integrity-Monitor

# Go to the demo folder
cd demo_files

# Make the demo script executable
chmod +x demo_script.sh

# Run the automated demo
./demo_script.sh
```

**What happens:** The script automatically creates files, creates a baseline, makes changes, and shows you the results.

### **Step 2: Try It Yourself (Recommended)**
After running the demo, try the commands manually:

```bash
# 1. Create a baseline for the sample files
fim init --path ./demo_files/sample_files

# 2. Make some changes to files
echo "Modified content" >> ./demo_files/sample_files/config.ini
echo "New file content" > ./demo_files/sample_files/newfile.txt
rm ./demo_files/sample_files/temp.txt

# 3. Check what changed
fim verify --path ./demo_files/sample_files

# 4. Export your results
fim export --format json --output demo_results.json
```

## 📁 **Sample Files Structure**

```
sample_files/
├── config.ini          # Configuration file
├── script.sh           # Executable script
├── data.txt            # Data file
├── temp.txt            # Temporary file (will be deleted during demo)
└── logs/
    ├── app.log         # Application log
    └── error.log       # Error log
```

## 📊 **What You Should See**

### **After Creating Baseline:**
```
Creating baseline for: ./demo_files/sample_files
[████████████████████████████████████████] 100%
Baseline created successfully with 6 files

┌─────────────────┬─────────────────────┐
│ Metric          │ Value               │
├─────────────────┼─────────────────────┤
│ Path            │ ./demo_files/sample_files │
│ Files Processed │ 6                   │
│ Database        │ fim.db              │
└─────────────────┴─────────────────────┘
```

### **After Making Changes:**
```
┌───────────┬───────┬─────────────────────────────────────┐
│ Status    │ Count │ Files                               │
├───────────┼───────┼─────────────────────────────────────┤
│ Created   │ 1     │ ./demo_files/sample_files/newfile.txt │
│ Modified  │ 1     │ ./demo_files/sample_files/config.ini  │
│ Deleted   │ 1     │ ./demo_files/sample_files/temp.txt    │
│ Unchanged │ 4     │                                     │
└───────────┴───────┴─────────────────────────────────────┘
```

## 🔧 **Troubleshooting the Demo**

### **Problem: "Permission denied"**
```bash
# Check if the script is executable
ls -la demo_script.sh

# Make it executable again
chmod +x demo_script.sh
```

### **Problem: "fim: command not found"**
```bash
# Go back to project root and reinstall
cd ..
pip3 install -e .
```

### **Problem: "Database is locked"**
```bash
# Remove the database and try again
rm -f demo_files/demo_fim.db
./demo_script.sh
```

## 📚 **Understanding the Demo**

### **What the Demo Script Does:**
1. **Creates sample files** - Sets up a realistic file structure
2. **Creates baseline** - Takes a snapshot of all files
3. **Makes changes** - Modifies, creates, and deletes files
4. **Detects changes** - Shows you what's different
5. **Exports results** - Saves data in JSON and CSV formats

### **Key Concepts Demonstrated:**
- **Baseline Creation**: Taking a "picture" of your files
- **Change Detection**: Finding differences between now and baseline
- **File Integrity**: Ensuring files haven't been tampered with
- **Reporting**: Getting clear, readable results

## 🎓 **Learning Path**

1. **Start with the demo script** - See how everything works automatically
2. **Try manual commands** - Understand each step individually
3. **Experiment with your own files** - Apply what you learned
4. **Read the main README** - Learn more advanced features

## 📝 **Next Steps**

After running the demo:
- Try monitoring a folder on your computer
- Experiment with different file types
- Learn about the export formats
- Check out the main project README for more details

## 🔒 **Important Notes**

- The demo creates a local database (`demo_fim.db`)
- All operations are logged for debugging
- Files are only read, never modified (except for demo purposes)
- This is for learning, not production use

---

**Ready to start?** Run `./demo_script.sh` and watch the magic happen! 🚀
