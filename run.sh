#!/bin/bash
# Quick run script that ensures Python 3.11 is used

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Technical Documentation Assistant${NC}"
echo -e "${BLUE}Using Python 3.11 with ChromaDB${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv311" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -m venv venv311"
    exit 1
fi

# Activate virtual environment and run
source venv311/bin/activate

# Verify Python version
PYTHON_VERSION=$(python --version)
echo -e "${GREEN}✓ Using: $PYTHON_VERSION${NC}"
echo ""

# Run Streamlit
streamlit run app.py
