#!/bin/bash

# UW Course Checker - Quick Start Script

echo "🎓 UW Course Checker - Setup and Run"
echo "===================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created. Please edit it with your settings."
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python3 -c "from src.database.database import Database; Database().initialize()" 2>/dev/null
echo "✓ Database initialized"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Available commands:"
echo "  python main.py monitor              # Start monitoring"
echo "  python main.py add [options]        # Add course to monitor"
echo "  python main.py check [options]      # Check a course once"
echo "  python main.py list                 # List active monitors"
echo "  python main.py history [options]    # View enrollment history"
echo "  python main.py test-notify          # Test notifications"
echo ""
echo "For more help: python main.py --help"
echo ""
