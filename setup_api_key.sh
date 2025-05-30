#!/bin/bash

# API Key Setup Script for RAG File Search System

echo "🚀 RAG File Search System - API Key Setup"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "📄 .env file already exists"
fi

echo ""
echo "🔑 OpenAI API Key Setup Required"
echo "--------------------------------"
echo ""
echo "To use this system, you need an OpenAI API key."
echo ""
echo "Steps to get your API key:"
echo "1. Go to: https://platform.openai.com/api-keys"
echo "2. Sign in or create an OpenAI account"
echo "3. Click 'Create new secret key'"
echo "4. Copy the generated key"
echo ""

# Check if API key is already set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  API key not configured yet!"
    echo ""
    read -p "Do you have your OpenAI API key ready? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "Enter your OpenAI API key: " -s api_key
        echo ""
        
        if [ ! -z "$api_key" ]; then
            # Replace the placeholder with the actual API key
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s/OPENAI_API_KEY=your_openai_api_key_here/OPENAI_API_KEY=$api_key/" .env
            else
                # Linux
                sed -i "s/OPENAI_API_KEY=your_openai_api_key_here/OPENAI_API_KEY=$api_key/" .env
            fi
            echo "✅ API key configured successfully!"
        else
            echo "❌ No API key provided. Please edit .env file manually."
        fi
    else
        echo ""
        echo "📝 Please edit the .env file and replace 'your_openai_api_key_here' with your actual API key."
    fi
else
    echo "✅ API key appears to be configured"
fi

echo ""
echo "🔍 Verifying setup..."

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $(basename $VIRTUAL_ENV)"
else
    echo "⚠️  No virtual environment detected"
    echo "   Recommendation: Run 'python -m venv venv && source venv/bin/activate'"
fi

# Check if dependencies are installed
if python -c "import flask, openai" 2>/dev/null; then
    echo "✅ Required dependencies installed"
else
    echo "⚠️  Missing dependencies. Run: pip install -r requirements.txt"
fi

echo ""
echo "🚀 Next Steps:"
echo "1. Ensure your API key is set in .env file"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Start the application: python app.py"
echo ""
echo "📖 For more information, see README.md"
