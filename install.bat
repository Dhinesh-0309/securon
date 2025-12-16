@echo off
REM Securon Platform Installation Script for Windows
REM This script installs the Securon platform and makes the 'securon' command available

echo 🚀 Installing Securon Platform...
echo ==================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

echo ✅ Python is available

REM Navigate to backend directory
cd backend

REM Install the package in development mode
echo 🔧 Installing Securon platform...
python -m pip install -e .

REM Verify installation
echo 🔍 Verifying installation...
securon --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Installation verification failed
    echo 💡 Try running: cd backend && pip install -e .
    pause
    exit /b 1
)

echo.
echo 🎉 Securon Platform installed successfully!
echo.
echo 📋 Available commands:
echo    securon --help                    # Show help
echo    securon rules stats               # Show rule statistics
echo    securon scan file ^<file.tf^>       # Scan a Terraform file
echo    securon scan directory ^<dir^>      # Scan a directory
echo    securon rules list                # List security rules
echo    securon rules export ^<file.md^>    # Export rules summary
echo.
echo 🔍 Try scanning the demo files:
echo    securon scan file demo/terraform/insecure-example.tf
echo    securon scan directory demo/terraform/
echo.
echo ✨ Happy scanning!
pause