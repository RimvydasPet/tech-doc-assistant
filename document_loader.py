from typing import List
import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from logger import logger
from config import CHUNK_SIZE, CHUNK_OVERLAP, OFFICIAL_DOC_URLS, DOC_FETCH_TIMEOUT_SECONDS, DOC_FETCH_USER_AGENT


class TechnicalDocumentLoader:
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents(self) -> List[Document]:
        logger.info("Loading technical documentation")

        session = requests.Session()
        session.headers.update({"User-Agent": DOC_FETCH_USER_AGENT})

        documents: List[Document] = []
        for library, urls in OFFICIAL_DOC_URLS.items():
            for url in urls:
                try:
                    response = session.get(url, timeout=DOC_FETCH_TIMEOUT_SECONDS)
                    response.raise_for_status()
                except Exception as e:
                    logger.warning(f"Failed to fetch {url}: {e}")
                    continue

                soup = BeautifulSoup(response.text, "lxml")
                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()

                text = soup.get_text("\n")
                lines = [line.strip() for line in text.splitlines()]
                cleaned = "\n".join([line for line in lines if line])

                if not cleaned:
                    continue

                documents.append(
                    Document(
                        page_content=cleaned,
                        metadata={
                            "source": url,
                            "library": library,
                        },
                    )
                )

        logger.info(f"Loaded {len(documents)} documents")

        if not documents:
            return []

        split_docs = self.text_splitter.split_documents(documents)
        logger.info(f"Split into {len(split_docs)} chunks")
        return split_docs
