# 🚀 Simple Setup Guide for Beginners

This guide will help you get the File Integrity Monitor running on your computer, even if you're new to programming.

## 📋 **What You Need**

- A computer (Windows, Mac, or Linux)
- Basic knowledge of using the command line/terminal
- Internet connection to download the project

## 🔍 **Step 1: Check What You Have**

### **Check if Python is installed:**
Open your terminal/command prompt and type:
```bash
python3 --version
```

**What you should see:**
- ✅ `Python 3.10.11` or higher = You're good to go!
- ❌ `command not found` = You need to install Python

### **Check if Git is installed:**
```bash
git --version
```

**What you should see:**
- ✅ `git version 2.x.x` = You're good to go!
- ❌ `command not found` = You need to install Git

## 🐍 **Step 2: Install Python (if needed)**

### **On Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click "Download Python 3.x.x"
3. Run the installer
4. **IMPORTANT:** Check "Add Python to PATH" during installation
5. Click "Install Now"

### **On Mac:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click "Download Python 3.x.x"
3. Run the installer
4. Follow the installation wizard

**Alternative (if you have Homebrew):**
```bash
brew install python3
```

### **On Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**On Linux (CentOS/RHEL):**
```bash
sudo yum install python3 python3-pip
```

## 📥 **Step 3: Install Git (if needed)**

### **On Windows:**
1. Go to [git-scm.com](https://git-scm.com/)
2. Download the installer
3. Run the installer with default settings

### **On Mac:**
1. Open Terminal
2. Run: `xcode-select --install`
3. This installs Git and other developer tools

**Alternative (if you have Homebrew):**
```bash
brew install git
```

### **On Linux:**
```bash
sudo apt install git  # Ubuntu/Debian
sudo yum install git  # CentOS/RHEL
```

## 📁 **Step 4: Download the Project**

### **Option A: Using Git (Recommended)**
```bash
# Download the project
git clone https://github.com/example/file-Integrity-Monitor.git

# Go into the project folder
cd file-Integrity-Monitor
```

### **Option B: Download as ZIP**
1. Go to the project page on GitHub
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file
5. Open terminal/command prompt in the extracted folder

## 🔧 **Step 5: Install the Project**

### **Install Python packages:**
```bash
# Install required packages
pip3 install -r requirements.txt

# Install the project itself
pip3 install -e .
```

**If you get permission errors:**
- **Windows:** Run Command Prompt as Administrator
- **Mac/Linux:** Try: `pip3 install --user -r requirements.txt`

### **Test the installation:**
```bash
fim version
```

**You should see:** `File Integrity Monitor v1.0.0`

## 🧪 **Step 6: Run Your First Test**

### **Create a test folder:**
```bash
# Make a test folder
mkdir my_test_files
cd my_test_files

# Create some test files
echo "Hello World" > file1.txt
echo "Test content" > file2.txt
```

### **Create your first baseline:**
```bash
# Go back to the project folder
cd ..

# Create a baseline
fim init --path ./my_test_files
```

**What this does:** Takes a "snapshot" of all your files.

### **Make some changes:**
```bash
# Go back to your test folder
cd my_test_files

# Modify a file
echo "Modified content" >> file1.txt

# Create a new file
echo "New file" > file3.txt
```

### **Check what changed:**
```bash
# Go back to the project folder
cd ..

# See what's different
fim verify --path ./my_test_files
```

## 🎬 **Step 7: Run the Demo (Optional but Recommended)**

The project comes with a ready-made demo:

```bash
# Go to demo folder
cd demo_files

# Make the demo script executable
chmod +x demo_script.sh

# Run the demo
./demo_script.sh
```

**What the demo does:**
1. Creates sample files
2. Creates a baseline
3. Makes changes to files
4. Shows you how to detect changes
5. Exports results

## 🔧 **Common Problems & Solutions**

### **Problem: "fim: command not found"**
**Solution:**
```bash
# Reinstall the project
pip3 install -e .

# Or run directly with Python
python3 -m fim.cli version
```

### **Problem: "Permission denied"**
**Solution:**
```bash
# Check permissions
ls -la /path/to/folder

# Use a folder you own
fim init --path ~/Documents
```

### **Problem: "No module named 'click'"**
**Solution:**
```bash
# Install dependencies
pip3 install -r requirements.txt

# Or install individually
pip3 install click rich
```

### **Problem: "Database is locked"**
**Solution:**
```bash
# Remove the database file
rm fim.db

# Run the command again
fim init --path /your/folder
```

## 📚 **What to Do Next**

1. **Practice with the demo** - Run it a few times to understand the workflow
2. **Try with your own files** - Monitor a folder you use regularly
3. **Read the main README** - Learn about advanced features
4. **Experiment with different file types** - See what the system can detect

## 🆘 **Still Having Trouble?**

### **Check the logs:**
```bash
# Look for error messages
tail -f fim.log
```

### **Run with verbose output:**
```bash
# See what's happening behind the scenes
fim init --path /your/folder --verbose
```

### **Start simple:**
```bash
# Test with your home directory
fim init --path ~/Desktop
```

## 🎯 **Success Checklist**

- [ ] Python 3.10+ is installed
- [ ] Git is installed (or you downloaded the ZIP)
- [ ] Project is downloaded and extracted
- [ ] Dependencies are installed (`pip3 install -r requirements.txt`)
- [ ] Project is installed (`pip3 install -e .`)
- [ ] `fim version` command works
- [ ] You can create a baseline (`fim init --path /some/folder`)
- [ ] You can verify changes (`fim verify --path /some/folder`)

## 🎉 **Congratulations!**

You've successfully set up the File Integrity Monitor! You can now:
- Monitor files for changes
- Create baselines of file systems
- Detect unauthorized modifications
- Export results for analysis

**Next step:** Try the demo, then experiment with your own files!

---

**Need more help?** Check the main README.md file for detailed documentation.
