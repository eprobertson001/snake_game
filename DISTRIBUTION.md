# Snake Game - Distribution Package

## Overview
This package contains everything needed to distribute the Snake Game as a standalone application.

## Distribution Options

### Option 1: Python Package (.whl)
Create a Python wheel package that can be installed with pip:

```bash
# Build the package
python setup.py bdist_wheel

# Install on any computer with Python
pip install dist/snake_game-1.0.0-py3-none-any.whl

# Run the game
snake-game
```

### Option 2: Standalone Executable (.exe)
Create a completely self-contained executable:

```bash
# Install build dependencies
pip install -r requirements.txt

# Build executable
python build_exe.py

# Distribute the entire 'dist' folder
# Run: SnakeGame.exe
```

### Option 3: Installer Package
Create a Windows installer (.msi):

```bash
# Build executable first
python build_exe.py

# Create installer
python create_installer.py
```

## What Gets Included

### Core Files:
- `snake_game.py` - Main game code
- `requirements.txt` - Dependencies
- `README.md` - Documentation
- `setup.py` - Package configuration

### Build Files:
- `build_exe.py` - Executable builder
- `create_installer.py` - Installer creator
- `MANIFEST.in` - Package manifest

### Distribution Outputs:
- `dist/` - Built packages and executables
- `build/` - Temporary build files

## System Requirements

### For Python Package:
- Python 3.7 or higher
- pip package manager

### For Standalone Executable:
- Windows 10/11 (64-bit)
- No Python installation required

## Installation Instructions

### For Recipients:

#### Option A: Python Users
1. Download the `.whl` file
2. Run: `pip install snake_game-1.0.0-py3-none-any.whl`
3. Run: `snake-game`

#### Option B: General Users
1. Download and extract the `SnakeGame_Portable.zip`
2. Double-click `SnakeGame.exe`
3. Enjoy!

#### Option C: Installer
1. Download `SnakeGameInstaller.msi`
2. Double-click to install
3. Find "Snake Game" in Start Menu

## Building Instructions

### Prerequisites:
```bash
pip install -r requirements.txt
```

### Build All Formats:
```bash
python build_all.py
```

This creates:
- Python wheel package
- Standalone executable  
- Windows installer
- Portable zip package

## File Sizes (Approximate)
- Python wheel: ~50 KB
- Standalone executable: ~25 MB
- Windows installer: ~30 MB
- Portable zip: ~25 MB

## Distribution Checklist

✅ Test on clean Windows machine  
✅ Verify no Python dependencies needed  
✅ Check antivirus compatibility  
✅ Test all control schemes (WASD/Arrows)  
✅ Verify level progression works  
✅ Confirm portal mechanics function  
✅ Test game restart/menu navigation
