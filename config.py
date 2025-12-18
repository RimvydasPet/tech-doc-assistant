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

OFFICIAL_DOC_URLS = {
    "pandas": [
        "https://pandas.pydata.org/docs/",
        "https://pandas.pydata.org/docs/user_guide/index.html",
    ],
    "numpy": [
        "https://numpy.org/doc/stable/",
        "https://numpy.org/doc/stable/user/absolute_beginners.html",
    ],
    "scikit-learn": [
        "https://scikit-learn.org/stable/",
        "https://scikit-learn.org/stable/user_guide.html",
    ],
    "matplotlib": [
        "https://matplotlib.org/stable/",
        "https://matplotlib.org/stable/users/index.html",
    ],
    "seaborn": [
        "https://seaborn.pydata.org/",
        "https://seaborn.pydata.org/tutorial.html",
    ],
    "requests": [
        "https://requests.readthedocs.io/en/latest/",
        "https://requests.readthedocs.io/en/latest/user/quickstart/",
    ],
    "flask": [
        "https://flask.palletsprojects.com/en/stable/",
        "https://flask.palletsprojects.com/en/stable/quickstart/",
    ],
    "django": [
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/intro/overview/",
    ],
    "fastapi": [
        "https://fastapi.tiangolo.com/",
        "https://fastapi.tiangolo.com/tutorial/",
    ],
    "sqlalchemy": [
        "https://docs.sqlalchemy.org/en/20/",
        "https://docs.sqlalchemy.org/en/20/tutorial/",
    ],
}

DOC_FETCH_TIMEOUT_SECONDS = 15
DOC_FETCH_USER_AGENT = "tech-doc-assistant/1.0"

# Validation
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")
