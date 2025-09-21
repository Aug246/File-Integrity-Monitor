# Simple File Integrity Monitor (FIM)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **simple and focused File Integrity Monitor** that creates baselines and verifies file changes. Perfect for learning about file security and demonstrating security tools!

## 🎯 **What This Project Does**

Think of this like a "file detective" that:
- **Takes a snapshot** of your files (creates a "baseline")
- **Watches for changes** and tells you what's different
- **Reports everything** in easy-to-read formats

## 🚀 **Quick Start (Step by Step)**

### **Step 1: Check Your System**
First, make sure you have Python installed:
```bash
python3 --version
```
You should see something like `Python 3.10.11` or higher.

**If you don't have Python:**
- **macOS**: Download from [python.org](https://www.python.org/downloads/)
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: Usually pre-installed, or run `sudo apt install python3`

### **Step 2: Download the Project**
```bash
# Download the project
git clone https://github.com/example/file-Integrity-Monitor.git

# Go into the project folder
cd file-Integrity-Monitor
```

**If you don't have git:**
- **macOS**: Install Xcode Command Line Tools: `xcode-select --install`
- **Windows**: Download from [git-scm.com](https://git-scm.com/)
- **Linux**: `sudo apt install git`

### **Step 3: Install Dependencies**
```bash
# Install the required packages
pip3 install -r requirements.txt

# Install the project itself
pip3 install -e .
```

**If you get permission errors:**
- Try: `pip3 install --user -r requirements.txt`
- Or: `sudo pip3 install -r requirements.txt`

### **Step 4: Test the Installation**
```bash
# Check if FIM is working
fim version
```
You should see: `File Integrity Monitor v1.0.0`

## 🧪 **Your First File Monitoring Session**

### **1. Create a Test Folder**
```bash
# Make a test folder
mkdir my_test_files
cd my_test_files

# Create some test files
echo "Hello World" > file1.txt
echo "Test content" > file2.txt
echo "Configuration" > config.ini
```

### **2. Create Your First Baseline**
```bash
# Go back to the project folder
cd ..

# Create a baseline (snapshot) of your test files
fim init --path ./my_test_files
```

**What this does:** Takes a "picture" of all your files, including their sizes, modification dates, and unique fingerprints (hashes).

### **3. Make Some Changes**
```bash
# Go back to your test folder
cd my_test_files

# Modify a file
echo "Modified content" >> file1.txt

# Create a new file
echo "New file" > file3.txt

# Delete a file
rm file2.txt
```

### **4. Check What Changed**
```bash
# Go back to the project folder
cd ..

# See what's different from your baseline
fim verify --path ./my_test_files
```

**What you'll see:** A table showing which files were created, modified, or deleted.

### **5. Export Your Results**
```bash
# Save your results to a file
fim export --format json --output my_results.json

# Or save as CSV for Excel
fim export --format csv --output my_results.csv
```

## 📋 **All Available Commands**

| Command | What It Does | Example |
|---------|-------------|---------|
| `fim init --path /folder` | Create baseline for a folder | `fim init --path /etc` |
| `fim verify --path /folder` | Check for changes | `fim verify --path /etc` |
| `fim status` | Show system status | `fim status` |
| `fim export --format json` | Export data as JSON | `fim export --format json` |
| `fim version` | Show version info | `fim version` |

## 🔧 **Common Problems & Solutions**

### **Problem: "fim: command not found"**
**Solution:** The command isn't in your PATH. Try:
```bash
# Reinstall the project
pip3 install -e .

# Or run directly with Python
python3 -m fim.cli version
```

### **Problem: "Permission denied"**
**Solution:** You don't have permission to read the folder. Try:
```bash
# Check permissions
ls -la /path/to/folder

# Use a folder you own
fim init --path ~/Documents
```

### **Problem: "Database is locked"**
**Solution:** Another process is using the database. Try:
```bash
# Remove the database file
rm fim.db

# Run the command again
fim init --path /your/folder
```

### **Problem: "No module named 'click'"**
**Solution:** Dependencies aren't installed. Try:
```bash
# Install dependencies
pip3 install -r requirements.txt

# Or install individually
pip3 install click rich
```

## 🔄 **Reset Project to Clean State**

After running demos or experiments, you can easily reset the project back to its clean state:

```bash
# Make the reset script executable (first time only)
chmod +x reset_project.sh

# Reset the project to clean state
./reset_project.sh
```

**What the reset script does:**
- Removes all generated files (databases, logs, exports)
- Clears Python cache and build artifacts
- Restores demo files to original state
- Verifies the clean state
- Prepares the project for fresh demos

**Perfect for:**
- Starting over after experiments
- Preparing for demonstrations
- Cleaning up before sharing
- Resetting for new users

## 📚 **Understanding the Output**

### **Baseline Creation Output:**
```
Creating baseline for: /path/to/folder
[████████████████████████████████████████] 100%
Baseline created successfully with 15 files

┌─────────────────┬─────────────────────┐
│ Metric          │ Value               │
├─────────────────┼─────────────────────┤
│ Path            │ /path/to/folder     │
│ Files Processed │ 15                  │
│ Database        │ fim.db              │
└─────────────────┴─────────────────────┘
```

### **Verification Output:**
```
┌───────────┬───────┬─────────────────────────────────────┐
│ Status    │ Count │ Files                               │
├───────────┼───────┼─────────────────────────────────────┤
│ Created   │ 2     │ /path/new1.txt, /path/new2.txt     │
│ Modified  │ 1     │ /path/changed.txt                  │
│ Deleted   │ 0     │                                     │
│ Unchanged │ 12    │                                     │
└───────────┴───────┴─────────────────────────────────────┘
```

## 🎯 **What This Project is Perfect For**

- **Learning** about file security and monitoring
- **Demonstrating** security tools to recruiters
- **Basic file change detection** needs
- **Educational purposes** and workshops
- **Understanding** how file integrity monitoring works

## 🚫 **What This Project Does NOT Do**

- ❌ Real-time monitoring (it's manual check-based)
- ❌ Complex configuration management
- ❌ Advanced threat detection
- ❌ Network monitoring
- ❌ Enterprise features

## 🤝 **Getting Help**

### **Check the Logs**
If something goes wrong, check the logs:
```bash
# Look for error messages
tail -f fim.log
```

### **Run with Verbose Output**
Get more detailed information:
```bash
# See what's happening behind the scenes
fim init --path /your/folder --verbose
```

### **Test with Simple Files First**
Start with a small folder you own:
```bash
# Test with your home directory
fim init --path ~/Desktop
```

## 🔒 **Security Note**

This tool is for **learning and demonstration**. It stores file information locally and doesn't send data anywhere. For production use, consider enterprise-grade solutions.

## 📄 **License**

This project is licensed under the MIT License.

---

**Built for simplicity and learning** 🎓

**Need help?** Start with the demo, then try monitoring a small folder you own!