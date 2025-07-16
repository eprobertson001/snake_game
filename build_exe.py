# Snake Game Executable Build Configuration

import PyInstaller.__main__
import os
import sys

def build_executable():
    """Build standalone executable using PyInstaller"""
    
    # PyInstaller arguments
    args = [
        '--onefile',                    # Create a single executable file
        '--windowed',                   # Hide console window (GUI app)
        '--name=SnakeGame',            # Name of the executable
        '--icon=game_icon.ico',        # Icon file (we'll create this)
        '--add-data=README.md;.',      # Include README
        '--distpath=dist',             # Output directory
        '--workpath=build',            # Build directory
        '--clean',                     # Clean previous builds
        'snake_game.py'                # Main Python file
    ]
    
    # Add console option for debugging if needed
    if '--debug' in sys.argv:
        args.remove('--windowed')
        args.append('--console')
    
    print("Building Snake Game executable...")
    print("This may take a few minutes...")
    
    PyInstaller.__main__.run(args)
    
    print("\n✅ Build complete!")
    print("📁 Executable location: dist/SnakeGame.exe")
    print("📦 Ready for distribution!")

if __name__ == "__main__":
    build_executable()
