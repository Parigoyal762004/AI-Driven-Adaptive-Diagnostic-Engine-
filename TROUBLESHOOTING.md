# Windows Installation Troubleshooting Guide

## 🔧 Common Installation Issues and Solutions

### Issue 1: "Rust" or "Cargo" Error with Python 3.13

**Error Message:**
```
Cargo, the Rust package manager, is not installed or is not on PATH.
This package requires Rust and Cargo to compile extensions.
```

**Why This Happens:**
- You're using Python 3.13 (the latest version)
- Some packages (pydantic-core) need Rust to compile from source
- Pre-built wheels aren't available for Python 3.13 yet for older package versions

**✅ SOLUTION (Choose One):**

#### Option A: Use the Fix Script (Recommended)
1. **Double-click: `fix-python313.bat`**
2. Wait for installation to complete
3. Then run `run.bat`

#### Option B: Manual Installation
```batch
REM Activate environment
venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install with newer compatible versions
pip install -r requirements.txt
```

#### Option C: Downgrade to Python 3.11 or 3.12
1. Uninstall Python 3.13
2. Download Python 3.11 from: https://www.python.org/downloads/release/python-31112/
3. Install (check "Add Python to PATH")
4. Run setup.bat again

---

### Issue 2: "pip" Not Recognized

**Error Message:**
```
'pip' is not recognized as an internal or external command
```

**✅ SOLUTION:**
```batch
REM Use python -m pip instead
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### Issue 3: MongoDB Connection Failed

**Error Message:**
```
Database connection error
ServerSelectionTimeoutError
```

**✅ SOLUTIONS:**

#### For MongoDB Atlas (Cloud):
1. Go to https://cloud.mongodb.com
2. Click on your cluster → "Connect"
3. Choose "Connect your application"
4. Copy the connection string
5. Edit `.env` file:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<username>` and `<password>` with your credentials
7. Make sure IP whitelist includes your IP or use `0.0.0.0/0` for testing

#### For Local MongoDB:
1. Download MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Install MongoDB
3. Start MongoDB service:
   - Open Services (Windows + R → services.msc)
   - Find "MongoDB Server"
   - Right-click → Start
4. Or run in command prompt: `mongod`
5. Use in `.env`:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   ```

---

### Issue 4: Permission Denied

**Error Message:**
```
PermissionError: [WinError 5] Access is denied
```

**✅ SOLUTIONS:**

1. **Run as Administrator:**
   - Right-click `setup.bat`
   - Choose "Run as administrator"

2. **Close other programs:**
   - Close any IDEs (VS Code, PyCharm)
   - Close command prompts
   - Try again

3. **Antivirus interference:**
   - Temporarily disable antivirus
   - Add folder to exclusions
   - Try installation again

---

### Issue 5: Port 8000 Already in Use

**Error Message:**
```
OSError: [WinError 10048] Only one usage of each socket address
```

**✅ SOLUTIONS:**

#### Option A: Use Different Port
Edit `run.bat`, change the last line to:
```batch
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

#### Option B: Kill Process Using Port 8000
```batch
REM Find process using port 8000
netstat -ano | findstr :8000

REM Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

---

### Issue 6: Virtual Environment Not Activating

**Error Message:**
```
'venv\Scripts\activate.bat' is not recognized
```

**✅ SOLUTION:**

1. **Delete and recreate:**
   ```batch
   rmdir /s /q venv
   python -m venv venv
   ```

2. **Use full path:**
   ```batch
   C:\path\to\adaptive-testing-engine\venv\Scripts\activate.bat
   ```

---

### Issue 7: Import Errors When Running

**Error Message:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**✅ SOLUTION:**

Virtual environment not activated properly:
```batch
REM Make sure you're in the project directory
cd C:\path\to\adaptive-testing-engine

REM Activate environment
venv\Scripts\activate.bat

REM Verify installation
pip list

REM Reinstall if needed
pip install -r requirements.txt
```

---

### Issue 8: Slow Installation

**✅ SOLUTIONS:**

1. **Increase timeout:**
   ```batch
   pip install --default-timeout=100 -r requirements.txt
   ```

2. **Use different mirror:**
   ```batch
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
   ```

3. **Install packages individually:**
   Run `fix-python313.bat` which installs one by one

---

## 🆘 Quick Diagnostic Commands

Run these in activated virtual environment to diagnose issues:

```batch
REM Check Python version
python --version

REM Check pip version
pip --version

REM Check if in virtual environment
where python

REM List installed packages
pip list

REM Check for package conflicts
pip check

REM Test MongoDB connection
python -c "from motor.motor_asyncio import AsyncIOMotorClient; print('Motor installed OK')"

REM Test FastAPI import
python -c "import fastapi; print('FastAPI installed OK')"
```

---

## 📋 Clean Reinstall Steps

If all else fails, start fresh:

```batch
REM 1. Delete virtual environment
rmdir /s /q venv

REM 2. Delete any __pycache__ folders
del /s /q __pycache__

REM 3. Delete installed marker
del venv\installed.txt

REM 4. Run setup again
setup.bat
```

---

## ✅ Verification Checklist

After fixing issues, verify everything works:

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All packages installed (run: `pip list`)
- [ ] MongoDB running (local or Atlas)
- [ ] `.env` file configured
- [ ] Database seeded (run: `seed.bat`)
- [ ] Server starts (run: `run.bat`)
- [ ] API docs accessible at http://localhost:8000/docs

---

## 🎯 Recommended Setup for Python 3.13

If you're using Python 3.13, follow this exact sequence:

1. **Run:** `setup.bat` (it will fail, that's OK)
2. **Run:** `fix-python313.bat` (this will fix the dependencies)
3. **Configure:** Edit `.env` file with your MongoDB connection
4. **Seed:** `seed.bat` (populate database)
5. **Start:** `run.bat` (start the server)

---

## 📞 Still Having Issues?

If none of these solutions work:

1. **Check Python version compatibility:**
   - Python 3.11.x - ✅ Fully compatible
   - Python 3.12.x - ✅ Fully compatible  
   - Python 3.13.x - ⚠️ Use `fix-python313.bat`

2. **Try manual installation:**
   ```batch
   venv\Scripts\activate.bat
   python -m pip install --upgrade pip wheel
   pip install fastapi uvicorn motor pydantic python-dotenv httpx
   ```

3. **Check the error logs:**
   - Look at the exact error message
   - Search for it in this guide
   - Error messages are usually very specific

4. **Verify system requirements:**
   - Windows 10 or 11
   - 64-bit operating system
   - At least 2GB free disk space
   - Active internet connection

---

**Last Updated:** For Python 3.13 compatibility with pre-built wheels
