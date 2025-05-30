#!/bin/bash

# RAG File Search System Setup Script
set -e

echo "🚀 Setting up RAG File Search System..."

# Check if Python 3.10+ is installed
python_version=$(python3 --version 2>&1 | grep -o '3\.[0-9]*' | head -1)
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [[ $major_version -lt 3 ]] || [[ $major_version -eq 3 && $minor_version -lt 10 ]]; then
    echo "❌ Python 3.10 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs uploads static/css static/js templates

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.development.example .env
    echo ""
    echo "🔑 IMPORTANT: Please edit .env file and add your OpenAI API key:"
    echo "OPENAI_API_KEY=your_api_key_here"
    echo ""
fi

# Make the script executable
chmod +x setup.sh

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Run the application:"
echo "   source .venv/bin/activate"
echo "   python app.py"
echo "3. Open http://localhost:5000 in your browser"
echo ""
echo "🐳 For Docker deployment:"
echo "   docker-compose up --build"
echo ""
echo "📖 For more information, see README.md"
