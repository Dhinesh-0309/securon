# Securon Platform - Complete Setup Guide 🛡️

Welcome! This guide will help you set up and run the complete Securon Platform on your laptop. The platform includes both a CLI tool and a web interface for cloud security scanning.

## 📋 Prerequisites

Before starting, make sure you have:

- **Python 3.9 or higher** installed
- **Node.js 16 or higher** installed (for the web interface)
- **Git** installed
- **Terminal/Command Prompt** access

### Check Your System

```bash
# Check Python version
python3 --version
# or on Windows
python --version

# Check Node.js version
node --version

# Check npm version
npm --version
```

## 🚀 Installation Steps

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd securon-platform
```

### Step 2: Install the Backend (CLI Tool)

Choose your preferred method:

#### Option A: Automatic Installation (Recommended)

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
install.bat
```

#### Option B: Manual Installation

```bash
cd backend
pip install -e .
cd ..
```

#### Option C: Python Installation Script

```bash
cd backend
python install.py
cd ..
```

### Step 3: Verify CLI Installation

```bash
securon --version
```

You should see the Securon version number if installation was successful.

### Step 4: Install the Web Interface

```bash
cd frontend
npm install
cd ..
```

## 🏃‍♀️ Running the Application

### Option 1: Run CLI Only

The CLI tool is ready to use immediately after installation:

```bash
# Quick test with demo files
securon scan file demo/terraform/insecure-example.tf --format summary

# Show all available commands
securon --help
```

### Option 2: Run Full Platform (CLI + Web Interface)

You need to run both the backend API server and the frontend web server:

#### Terminal 1 - Start Backend API Server

```bash
cd backend
python -m securon.api.main
```

The backend API will start on `http://localhost:8000`

#### Terminal 2 - Start Frontend Web Server

```bash
cd frontend
npm start
```

The web interface will open automatically at `http://localhost:3000`

## 🔍 Testing Your Installation

### Test the CLI

```bash
# Show rule statistics
securon rules stats

# Scan a demo file
securon scan file demo/terraform/insecure-example.tf

# Scan entire demo directory
securon scan directory demo/terraform/ --format summary

# List all security rules
securon rules list
```

### Test the Web Interface

1. Open your browser to `http://localhost:3000`
2. You should see the Securon dashboard
3. Try uploading a Terraform file or using the demo files
4. Check that scanning results appear correctly

## 📁 Project Structure

```
securon-platform/
├── backend/                 # Python backend & CLI
│   ├── src/securon/        # Main package
│   ├── data/rules/         # 132+ security rules
│   ├── tests/              # Test suite
│   └── securon_cli.py      # CLI entry point
├── frontend/               # React web interface
│   ├── src/                # React components
│   ├── public/             # Static files
│   └── package.json        # Dependencies
├── demo/                   # Demo Terraform files
│   └── terraform/          # Sample files to test
├── install.sh             # Linux/macOS installer
├── install.bat            # Windows installer
└── README.md              # Project overview
```

## 🛠️ Development Mode

If you want to modify the code:

### Backend Development

```bash
cd backend
# Install in development mode (already done if you used install scripts)
pip install -e .

# Run tests
pytest tests/ -v

# Start API server with auto-reload
python -m securon.api.main --reload
```

### Frontend Development

```bash
cd frontend
# Start with hot reload
npm start

# Build for production
npm run build
```

## 🔧 Troubleshooting

### Common Issues

#### "securon command not found"

```bash
# Try reinstalling
cd backend
pip install -e .

# Or use direct path
python securon_cli.py --help
```

#### "Module not found" errors

```bash
# Make sure you're in the right directory
cd backend
pip install -r requirements.txt
pip install -e .
```

#### Frontend won't start

```bash
cd frontend
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

#### Backend API connection issues

- Make sure backend is running on port 8000
- Check that frontend proxy is configured correctly
- Verify no firewall is blocking the ports

### Port Conflicts

If ports 3000 or 8000 are already in use:

**Frontend (change from 3000):**
```bash
PORT=3001 npm start
```

**Backend (change from 8000):**
Edit the backend configuration or use environment variables.

## 🎯 What You Can Do Now

### CLI Usage
- Scan Terraform files for security issues
- Manage security rules (132+ built-in rules)
- Export security reports
- Integrate with CI/CD pipelines

### Web Interface Usage
- Upload and scan Terraform files
- View detailed security reports
- Manage security rules through UI
- Dashboard with security metrics

### Demo Files
- Test with provided demo files in `demo/terraform/`
- See examples of secure vs insecure configurations
- Learn about different security rule categories

## 📚 Next Steps

1. **Read the CLI Reference**: Check `CLI_REFERENCE.md` for all available commands
2. **Explore Demo Files**: Try scanning files in `demo/terraform/`
3. **Check Security Rules**: Run `securon rules list` to see all 132+ rules
4. **Web Interface**: Explore the dashboard at `http://localhost:3000`
5. **Integration**: Learn how to integrate with your CI/CD pipeline

## 🆘 Getting Help

- **CLI Help**: Run `securon --help` or `securon <command> --help`
- **Demo Files**: Check `demo/DEMO_FILES_README.md`
- **Security Rules**: See `demo/SECURITY_RULES_SUMMARY.md`
- **Issues**: Check the GitHub repository issues section

## 🎉 Success!

If you can run these commands successfully, you're all set:

```bash
# CLI working
securon --version
securon scan file demo/terraform/insecure-example.tf --format summary

# Web interface working (if running full platform)
# Open http://localhost:3000 in your browser
```

**Happy scanning! 🛡️✨**