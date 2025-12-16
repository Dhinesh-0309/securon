#!/usr/bin/env python3
"""
Securon Platform Installation Script

This script installs the Securon platform and makes the 'securon' command available globally.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version {sys.version.split()[0]} is compatible")

def install_securon():
    """Install the Securon platform"""
    print("🚀 Installing Securon Platform...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Get the current directory (should be backend/)
    current_dir = Path.cwd()
    print(f"📁 Installation directory: {current_dir}")
    
    # Check if we're in the right directory
    if not (current_dir / "pyproject.toml").exists():
        print("❌ pyproject.toml not found. Please run this script from the backend/ directory")
        sys.exit(1)
    
    # Install in development mode so changes are reflected immediately
    result = run_command(
        f"{sys.executable} -m pip install -e .",
        "Installing Securon platform in development mode"
    )
    
    if result is None:
        print("❌ Installation failed")
        sys.exit(1)
    
    # Verify installation
    result = run_command("securon --version", "Verifying installation")
    
    if result is None:
        print("❌ Installation verification failed")
        print("💡 Try running: pip install -e . manually")
        sys.exit(1)
    
    print("\n🎉 Securon Platform installed successfully!")
    print("\n📋 Available commands:")
    print("   securon --help                    # Show help")
    print("   securon rules stats               # Show rule statistics")
    print("   securon scan file <file.tf>       # Scan a Terraform file")
    print("   securon scan directory <dir>      # Scan a directory")
    print("   securon rules list                # List security rules")
    print("   securon rules export <file.md>    # Export rules summary")
    print("\n🔍 Try scanning the demo files:")
    print("   securon scan file ../demo/terraform/insecure-example.tf")
    print("   securon scan directory ../demo/terraform/")
    print("\n✨ Happy scanning!")

if __name__ == "__main__":
    install_securon()