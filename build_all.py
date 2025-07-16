"""
Complete build script for all distribution formats
Creates Python package, executable, and installer
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for dir_pattern in dirs_to_clean:
        for path in Path('.').glob(dir_pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"🧹 Cleaned {path}")

def build_python_package():
    """Build Python wheel package"""
    print("\n📦 Building Python Package...")
    
    # Build wheel with proper path
    if not run_command("python setup.py bdist_wheel", "Building wheel package"):
        return False
    
    print("✅ Python package created in dist/")
    return True

def build_executable():
    """Build standalone executable"""
    print("\n🔧 Building Standalone Executable...")
    
    # Check if snake_game.py exists
    if not os.path.exists("snake_game.py"):
        print("❌ snake_game.py not found in current directory")
        return False
    
    # Install PyInstaller if not available
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        if not run_command("pip install pyinstaller", "Installing PyInstaller"):
            return False
    
    # Build executable with current directory
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name=SnakeGame",
        "--distpath=dist",
        "--workpath=build",
        "--clean",
        "snake_game.py"
    ]
    
    if not run_command(" ".join(pyinstaller_cmd), "Building executable"):
        return False
    
    print("✅ Executable created: dist/SnakeGame.exe")
    return True

def create_portable_package():
    """Create portable zip package"""
    print("\n📁 Creating Portable Package...")
    
    if not os.path.exists("dist/SnakeGame.exe"):
        print("❌ Executable not found. Build executable first.")
        return False
    
    # Create portable folder structure
    portable_dir = "dist/SnakeGame_Portable"
    os.makedirs(portable_dir, exist_ok=True)
    
    # Copy executable
    shutil.copy2("dist/SnakeGame.exe", portable_dir)
    
    # Copy documentation
    if os.path.exists("README.md"):
        shutil.copy2("README.md", portable_dir)
    
    # Create run instructions
    instructions = """# Snake Game - Portable Version

## How to Play:
1. Double-click SnakeGame.exe to start
2. Use Arrow Keys or WASD to move
3. Eat apples to grow and score points
4. Reach 10 apples to unlock the portal
5. Guide your snake through the portal to advance levels

## Controls:
- Arrow Keys or WASD: Move snake
- SPACE: Pause/Resume game
- R: Restart (when game over)
- M: Return to menu (when game over) 
- ESC: Quit game

## Features:
✅ Progressive levels with obstacles
✅ Portal-based level advancement  
✅ Smooth graphics and animations
✅ Multiple control schemes
✅ No installation required!

Enjoy playing Snake Game!
"""
    
    with open(f"{portable_dir}/HOW_TO_PLAY.txt", "w") as f:
        f.write(instructions)
    
    # Create zip package
    zip_path = "dist/SnakeGame_Portable.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, "dist")
                zipf.write(file_path, arc_path)
    
    print(f"✅ Portable package created: {zip_path}")
    return True

def create_installer_script():
    """Create NSIS installer script"""
    nsis_script = '''
; Snake Game Installer Script
!define APPNAME "Snake Game"
!define APPVERSION "1.0.0"
!define APPEXE "SnakeGame.exe"

Name "${APPNAME}"
OutFile "dist/SnakeGameInstaller.exe"
InstallDir "$PROGRAMFILES\\${APPNAME}"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Main Application"
    SetOutPath $INSTDIR
    File "dist\\SnakeGame.exe"
    File "README.md"
    
    ; Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\${APPEXE}"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    
    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\${APPEXE}"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    ; Add to Add/Remove Programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\${APPEXE}"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\${APPNAME}"
    Delete "$DESKTOP\\${APPNAME}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
SectionEnd
'''
    
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    return True

def main():
    """Main build process"""
    print("🚀 Snake Game - Complete Build Process")
    print("=" * 50)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build all formats
    success_count = 0
    total_builds = 3
    
    if build_python_package():
        success_count += 1
    
    if build_executable():
        success_count += 1
        
        if create_portable_package():
            success_count += 1
    
    # Create installer script (requires NSIS to actually build)
    create_installer_script()
    print("\n📝 Installer script created: installer.nsi")
    print("   (Requires NSIS to build actual installer)")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎉 Build Complete! ({success_count}/{total_builds} successful)")
    
    if os.path.exists("dist"):
        print("\n📂 Distribution files created:")
        for item in os.listdir("dist"):
            size = os.path.getsize(f"dist/{item}")
            size_mb = size / (1024 * 1024)
            print(f"   📄 {item} ({size_mb:.1f} MB)")
    
    print("\n🎮 Your Snake Game is ready for distribution!")
    print("\nDistribution options:")
    print("   • Python users: Install the .whl file")
    print("   • General users: Use the .exe or portable .zip")
    print("   • Enterprise: Create installer with NSIS")

if __name__ == "__main__":
    main()
