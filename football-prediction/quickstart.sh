#!/bin/bash

# Football Prediction System - Quick Start Script

echo "======================================================================"
echo "FOOTBALL PREDICTION SYSTEM v3.0 - Quick Start"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.10 or later."
    exit 1
fi
echo "✅ Python OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi
echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Setup environment
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
    echo ""
else
    echo "ℹ️  .env file already exists"
    echo ""
fi

# Create directories
echo "Creating necessary directories..."
mkdir -p predictions
mkdir -p logs
mkdir -p models_ml
echo "✅ Directories created"
echo ""

# Database setup
echo "======================================================================"
echo "DATABASE SETUP"
echo "======================================================================"
echo ""
echo "To setup the database, run:"
echo "  python scripts/setup_database.py"
echo ""

# Test system
echo "======================================================================"
echo "TESTING INSTALLATION"
echo "======================================================================"
echo ""
echo "To test the system, run:"
echo "  python scripts/test_system.py"
echo ""

# Quick start example
echo "======================================================================"
echo "QUICK START EXAMPLE"
echo "======================================================================"
echo ""
echo "1. Setup database:"
echo "   python scripts/setup_database.py"
echo ""
echo "2. Configure API keys in .env file"
echo ""
echo "3. Run a test prediction (example match ID):"
echo "   python src/pipeline.py 1035480"
echo ""
echo "4. Start automated scheduler:"
echo "   python src/scheduler.py"
echo ""

echo "======================================================================"
echo "✅ Quick start complete!"
echo "======================================================================"
echo ""
echo "For more information, see README.md"
echo ""
