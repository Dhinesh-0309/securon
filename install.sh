#!/bin/bash

# Securon Platform Installation Script
# This script installs the Securon platform and makes the 'securon' command available

set -e

echo "🚀 Installing Securon Platform..."
echo "=================================="

# Check if Python 3.9+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.9 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version $PYTHON_VERSION is compatible"

# Navigate to backend directory
cd backend

# Install the package in development mode
echo "🔧 Installing Securon platform..."
python3 -m pip install -e .

# Verify installation
echo "🔍 Verifying installation..."
if securon --version > /dev/null 2>&1; then
    echo "✅ Installation successful!"
else
    echo "❌ Installation verification failed"
    echo "💡 Try running: cd backend && pip install -e ."
    exit 1
fi

echo ""
echo "🎉 Securon Platform installed successfully!"
echo ""
echo "📋 Available commands:"
echo "   securon --help                    # Show help"
echo "   securon rules stats               # Show rule statistics"
echo "   securon scan file <file.tf>       # Scan a Terraform file"
echo "   securon scan directory <dir>      # Scan a directory"
echo "   securon rules list                # List security rules"
echo "   securon rules export <file.md>    # Export rules summary"
echo ""
echo "🔍 Try scanning the demo files:"
echo "   securon scan file demo/terraform/insecure-example.tf"
echo "   securon scan directory demo/terraform/"
echo ""
echo "✨ Happy scanning!"