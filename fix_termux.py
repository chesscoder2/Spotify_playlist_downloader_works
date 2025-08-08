#!/usr/bin/env python3
"""
Termux Compatibility Fix
Run this if you get urllib3/requests errors
"""

import subprocess
import sys
import os

def fix_dependencies():
    """Fix common Termux compatibility issues"""
    print("🔧 Fixing Termux compatibility issues...")
    
    # Fix urllib3/requests compatibility
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 
            'urllib3==1.26.18', 'requests==2.31.0'
        ], check=True)
        print("✅ Fixed urllib3/requests compatibility")
    except:
        print("⚠️  Could not fix urllib3/requests - trying alternative")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--force-reinstall',
                'spotipy', 'requests', 'urllib3'
            ], check=True)
        except:
            pass
    
    # Ensure all dependencies are installed
    deps = [
        'spotipy>=2.22.1',
        'yt-dlp>=2024.1.1', 
        'mutagen>=1.46.0',
        'pillow>=10.0.0',
        'requests>=2.31.0',
        'python-dotenv>=1.0.0',
        'psutil>=5.9.0',
        'tqdm>=4.65.0',
        'colorama>=0.4.6'
    ]
    
    print("📦 Installing/updating dependencies...")
    for dep in deps:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', dep
            ], check=True, capture_output=True)
            print(f"✅ {dep.split('>=')[0]}")
        except:
            print(f"⚠️  {dep.split('>=')[0]} - using existing version")
    
    print("\n✅ Termux compatibility fix completed!")
    print("Now try running: python main.py")

if __name__ == "__main__":
    fix_dependencies()