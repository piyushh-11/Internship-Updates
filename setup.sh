#!/bin/bash

# GitHub Internship Notifier Setup Script
# This script sets up the virtual environment and installs dependencies

echo "🚀 Setting up GitHub Internship Job Tracker for Discord..."
echo "================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created! Please edit it with your credentials."
else
    echo "⚠️ .env file already exists, skipping creation."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your credentials:"
echo "   - GitHub Personal Access Token"
echo "   - Discord Bot Token"
echo "   - Discord Channel ID"
echo ""
echo "2. Run the notifier:"
echo "   source venv/bin/activate"
echo "   python notifier.py"
echo ""
echo "📖 For detailed setup instructions, see the instructions.txt file." 