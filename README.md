# 📚 Technical Documentation Assistant

AI-powered chatbot for Python library documentation. Built with Google Gemini, LangChain, and ChromaDB vector search.

## 🌟 Features

- **RAG (Retrieval Augmented Generation)**: Query translation, decomposition, and hybrid retrieval
- **Vector Search**: ChromaDB-based semantic search with Google embeddings
- **Code Execution**: Safe Python code execution (RestrictedPython)
- **Package Info**: Real-time PyPI package information
- **Documentation Links**: Get official documentation links for supported Python libraries (plus common sections like install/tutorial/API)
- **Visual Answers (Optional)**: The assistant can return a JSON response with an accompanying table/chart that the UI renders
- **Supported Libraries**: pandas, numpy, scikit-learn, matplotlib, seaborn, requests, flask, django, fastapi, sqlalchemy

## 🚀 Quick Start

### Prerequisites
- **Python 3.11 or 3.12** (ChromaDB requires Python < 3.14)

### 1. Set Up Python 3.11 Environment
```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv_py311

# Activate it
source venv_py311/bin/activate  # On Mac/Linux
# or
venv_py311\Scripts\activate     # On Windows

# Or use the setup script
./setup_py311.sh
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get Google API Key
1. Visit https://makersuite.google.com/app/apikey
2. Create an API key
3. Create a `.env` file (you can copy the template):
```bash
cp .env.example .env

# Edit .env and set:
GOOGLE_API_KEY=your_key_here
```

### 4. Run the App

**Option 1: Use the run script (Recommended)**
```bash
./run.sh
```

**Option 2: Manual activation**
```bash
source venv_py311/bin/activate
streamlit run app.py
```

**⚠️ IMPORTANT**: Ensure you run Streamlit using the same Python environment where you installed dependencies (recommended: `venv_py311`).

Open http://localhost:8501 in your browser.

## 💡 Usage Examples

- "How do I create a pandas DataFrame?"
- "Execute: import pandas as pd; print(pd.__version__)"
- "What's the latest version of numpy?"
- "Find matplotlib plotting documentation"
- "Show a table comparing numpy arrays vs Python lists" (then enable **Visual Answers** in the sidebar)

## 🏗️ Project Structure

```
tech-doc-assistant/
├── app.py                    # Streamlit UI
├── chatbot.py               # Main chatbot engine
├── rag_engine.py            # Advanced RAG implementation
├── vector_db.py             # Vector database management
├── document_loader.py       # Knowledge base loader
├── tools.py                 # Tool implementations
├── config.py                # Configuration settings
├── logger.py                # Logging setup
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## ⚙️ Configuration

Edit `config.py` to customize model, RAG parameters, rate limits, and supported libraries.

In the UI sidebar you can also toggle:
- Tool calling
- Visual answers

## 🐛 Troubleshooting

- **"GOOGLE_API_KEY not found"**: Add valid key to `.env` file
- **Vector DB fails**: Delete `chroma_db/` folder and restart
- **View logs**: `tail -f chatbot.log`

---

**Tech Stack**: Google Gemini 2.5 Flash • LangChain • ChromaDB • Streamlit • Python 3.11
