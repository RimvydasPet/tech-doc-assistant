# 📚 Technical Documentation Assistant

AI-powered chatbot for Python library documentation. Built with Google Gemini, LangChain, and ChromaDB vector search.

## 🌟 Features

- **RAG (Retrieval Augmented Generation)**: Query translation, decomposition, and hybrid retrieval
- **Vector Search**: ChromaDB-based semantic search with Google embeddings
- **Multi-Language Support**: Interact in 10+ languages (English, Spanish, French, German, Chinese, Japanese, Portuguese, Russian, Italian, Korean) with automatic detection or manual selection
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
python-docs-copilot/
├── app.py                    # Streamlit UI (sidebar, chat interface, visual rendering, language selection)
├── chatbot.py                # Main chatbot engine (tool detection, execution, response generation)
├── language_handler.py       # Multi-language support (detection, translation)
├── rag_engine.py             # Advanced RAG (query translation, decomposition, multi-query retrieval)
├── vector_db.py              # ChromaDB vector database management
├── document_loader.py        # Knowledge base document loader
├── tools.py                  # Tool implementations (CodeExecutor, PackageInfoFetcher, DocumentationSearcher)
├── rate_limiter.py           # Rate limiting implementation (sliding window algorithm)
├── config.py                 # Configuration (API keys, models, supported libraries, doc URLs)
├── logger.py                 # Logging setup
├── requirements.txt          # Python dependencies
├── run.sh                    # Run script (auto-detects Python 3.11 venv)
├── setup_py311.sh            # Setup script for Python 3.11 environment
├── .env.example              # Environment variables template
├── .env                      # Your API keys (not in git)
├── .gitignore                # Git ignore rules
├── chroma_db/                # Vector database storage (auto-generated)
├── chatbot.log               # Application logs
└── README.md                 # This file
```

## ⚙️ Configuration

Edit `config.py` to customize:
- **Model settings**: Google Gemini model, embedding model
- **RAG parameters**: Chunk size, overlap, top-k results
- **Rate limits**: Max requests per minute (default: 20)
- **Token limits**: Max tokens per request (default: 4000)
- **Supported libraries**: List of libraries for documentation search

In the UI sidebar you can:
- Toggle tool calling
- Toggle visual answers
- Select language (auto-detect or manual selection)
- View rate limit status (requests used/remaining)

## 🌍 Multi-Language Support

The chatbot supports interaction in 10+ languages:
- **English** (en)
- **Spanish** / Español (es)
- **French** / Français (fr)
- **German** / Deutsch (de)
- **Chinese** / 中文 (zh)
- **Japanese** / 日本語 (ja)
- **Portuguese** / Português (pt)
- **Russian** / Русский (ru)
- **Italian** / Italiano (it)
- **Korean** / 한국어 (ko)

### How It Works:
1. **Auto-Detection** (default): The system automatically detects your language
2. **Manual Selection**: Choose your preferred language from the sidebar
3. **Translation Pipeline**: 
   - Your query is translated to English for RAG retrieval
   - The response is generated in English
   - The response is translated back to your language

### Example Queries in Different Languages:
- 🇪🇸 "¿Cómo crear un DataFrame de pandas?"
- 🇫🇷 "Comment créer un DataFrame pandas?"
- 🇩🇪 "Wie erstelle ich einen pandas DataFrame?"
- 🇨🇳 "如何创建pandas DataFrame？"
- 🇯🇵 "pandasのDataFrameを作成する方法は？"

## 🐛 Troubleshooting

- **"GOOGLE_API_KEY not found"**: Add valid key to `.env` file
- **Vector DB fails**: Delete `chroma_db/` folder and restart
- **View logs**: `tail -f chatbot.log`

---

**Tech Stack**: Google Gemini 2.5 Flash • LangChain • ChromaDB • Streamlit • Python 3.11
