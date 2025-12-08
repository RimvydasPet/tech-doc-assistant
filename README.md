# 📚 Technical Documentation Assistant

AI-powered chatbot for Python library documentation. Built with Google Gemini, LangChain, and FAISS vector search.

## 🌟 Features

- **RAG (Retrieval Augmented Generation)**: Query translation, decomposition, and hybrid retrieval
- **Vector Search**: FAISS-based semantic search with Google embeddings
- **Code Execution**: Safe Python code execution (RestrictedPython)
- **Package Info**: Real-time PyPI package information
- **Documentation Search**: Find official docs for Python libraries
- **Supported Libraries**: pandas, numpy, scikit-learn, matplotlib, seaborn, requests, flask, django, fastapi, sqlalchemy

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Google API Key
1. Visit https://makersuite.google.com/app/apikey
2. Create an API key
3. Add to `.env` file:
```bash
GOOGLE_API_KEY=your_key_here
```

### 3. Run
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## 💡 Usage Examples

- "How do I create a pandas DataFrame?"
- "Execute: import pandas as pd; print(pd.__version__)"
- "What's the latest version of numpy?"
- "Find matplotlib plotting documentation"

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

## 🐛 Troubleshooting

- **"GOOGLE_API_KEY not found"**: Add valid key to `.env` file
- **Vector DB fails**: Delete `chroma_db/` folder and restart
- **View logs**: `tail -f chatbot.log`

## 📚 Additional Documentation

- **PYTHON_3.14_NOTES.md**: Python 3.14 compatibility notes
- **MIGRATION_GUIDE.md**: OpenAI to Google Gemini migration guide

---

**Tech Stack**: Google Gemini 2.5 Flash • LangChain • FAISS • Streamlit • Python 3.14
