#!/bin/bash
# Setup script for Python 3.11 environment with ChromaDB

echo "🔧 Setting up Python 3.11 environment for ChromaDB..."

# Activate virtual environment
source venv_py311/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv_py311/bin/activate"
echo ""
echo "To run the app:"
echo "  streamlit run app.py"
