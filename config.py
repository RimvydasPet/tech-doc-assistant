import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_MODEL = "gemini-2.5-flash"  # Updated to latest available model
EMBEDDING_MODEL = "models/text-embedding-004"  # Updated embedding model

# Vector Database Configuration
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "tech_docs"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = 20
MAX_TOKENS_PER_REQUEST = 4000

# Tool Execution Configuration
CODE_EXECUTION_TIMEOUT = 10  # seconds
MAX_CODE_LENGTH = 1000  # characters

# Logging Configuration
LOG_FILE = "chatbot.log"
LOG_LEVEL = "INFO"

# Supported Python Libraries (for documentation)
SUPPORTED_LIBRARIES = [
    "pandas",
    "numpy",
    "scikit-learn",
    "matplotlib",
    "seaborn",
    "requests",
    "flask",
    "django",
    "fastapi",
    "sqlalchemy"
]

# Validation
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
