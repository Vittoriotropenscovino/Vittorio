#!/bin/bash

echo "============================================================"
echo "Installation Test Script"
echo "============================================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "2. Creating virtual environment..."
python3 -m venv venv

# Activate and install
echo ""
echo "3. Installing dependencies (this may take a few minutes)..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "============================================================"
echo "Installation Complete!"
echo "============================================================"
echo ""
echo "To activate the environment and run tests:"
echo "  source venv/bin/activate"
echo "  python3 test_quick.py"
echo ""
