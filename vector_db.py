import os
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from document_loader import TechnicalDocumentLoader
from logger import logger
from config import CHROMA_DB_DIR, COLLECTION_NAME, EMBEDDING_MODEL, GOOGLE_API_KEY

class VectorDatabase:
    
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY
        )
        self.vectorstore: Optional[Chroma] = None
        # Initialize ChromaDB client with proper settings for v0.5+
        self.client = None
        
    def initialize(self, force_reload: bool = False) -> None:
        logger.info("Initializing vector database")
        
        # Create ChromaDB client with settings
        os.makedirs(CHROMA_DB_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=CHROMA_DB_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Check if database exists
        db_exists = os.path.exists(CHROMA_DB_DIR) and os.path.isdir(CHROMA_DB_DIR)
        
        if db_exists and not force_reload:
            logger.info("Loading existing ChromaDB vector database")
            try:
                self.vectorstore = Chroma(
                    client=self.client,
                    collection_name=COLLECTION_NAME,
                    embedding_function=self.embeddings
                )
                logger.info("ChromaDB loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load existing database: {e}. Creating new one.")
                self._create_database()
        else:
            logger.info("Creating new ChromaDB vector database")
            self._create_database()
    
    def _create_database(self) -> None:
        # Load documents
        loader = TechnicalDocumentLoader()
        documents = loader.load_documents()
        
        # Create vector store with ChromaDB using the client
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            client=self.client,
            collection_name=COLLECTION_NAME
        )
        
        logger.info(f"ChromaDB vector database created with {len(documents)} document chunks")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if not self.vectorstore:
            raise ValueError("Vector database not initialized")
        
        logger.info(f"Performing similarity search for: {query[:50]}...")
        results = self.vectorstore.similarity_search(query, k=k)
        logger.info(f"Found {len(results)} results")
        
        return results
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        if not self.vectorstore:
            raise ValueError("Vector database not initialized")
        
        logger.info(f"Performing similarity search with scores for: {query[:50]}...")
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        logger.info(f"Found {len(results)} results")
        
        return results
    
    def add_documents(self, documents: List[Document]) -> None:
        if not self.vectorstore:
            raise ValueError("Vector database not initialized")
        
        logger.info(f"Adding {len(documents)} documents to vector database")
        self.vectorstore.add_documents(documents)
        logger.info("Documents added successfully")
    
    def get_retriever(self, search_kwargs: Optional[dict] = None):
        if not self.vectorstore:
            raise ValueError("Vector database not initialized")
        
        if search_kwargs is None:
            search_kwargs = {"k": 5}
        
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
