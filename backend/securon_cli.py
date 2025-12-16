#!/usr/bin/env python3
"""
Securon CLI Entry Point

This script provides a command-line interface for the Securon platform,
allowing users to scan Terraform files and manage security rules.

Usage:
    python securon_cli.py scan file terraform/main.tf
    python securon_cli.py scan directory terraform/
    python securon_cli.py rules list --status active
    python securon_cli.py rules approve rule-123
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from securon.cli.main import cli_main

if __name__ == '__main__':
    sys.exit(cli_main())