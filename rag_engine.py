"""RAG engine with query translation and multi-query retrieval."""
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from vector_db import VectorDatabase
from logger import logger
from config import GOOGLE_API_KEY, GOOGLE_MODEL, TOP_K_RESULTS


class AdvancedRAGEngine:
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
        self.llm = ChatGoogleGenerativeAI(
            model=GOOGLE_MODEL,
            temperature=0,
            google_api_key=GOOGLE_API_KEY
        )
        
        # Query translation prompt
        self.query_translation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at translating user questions about Python libraries 
            into optimized search queries. Given a user question, generate 3 different search queries 
            that would help find relevant documentation. Each query should approach the question from 
            a different angle.
            
            Return the queries as a JSON array of strings."""),
            ("human", "{question}")
        ])
        
        # Query decomposition prompt
        self.query_decomposition_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at breaking down complex questions into simpler sub-questions.
            Given a complex question about Python libraries, break it down into 2-3 simpler questions
            that, when answered together, would provide a complete answer to the original question.
            
            Return the sub-questions as a JSON array of strings."""),
            ("human", "{question}")
        ])
    
    def translate_query(self, question: str) -> List[str]:
        logger.info(f"Translating query: {question[:50]}...")
        
        try:
            chain = self.query_translation_prompt | self.llm
            response = chain.invoke({"question": question})
            
            # Parse the response
            import json
            import re
            
            # Try to extract JSON from the response
            content = response.content.strip()
            
            # If response is wrapped in markdown code blocks, extract it
            if content.startswith("```"):
                # Extract content between code blocks
                match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
                if match:
                    content = match.group(1)
            
            queries = json.loads(content)
            
            # Ensure it's a list
            if not isinstance(queries, list):
                queries = [question]
            
            logger.info(f"Generated {len(queries)} query variations")
            return queries
            
        except Exception as e:
            logger.warning(f"Error in query translation: {str(e)}. Using original question.")
            # Fallback to original question
            return [question]
    
    def decompose_query(self, question: str) -> List[str]:
        logger.info(f"Decomposing query: {question[:50]}...")
        
        try:
            chain = self.query_decomposition_prompt | self.llm
            response = chain.invoke({"question": question})
            
            # Parse the response
            import json
            import re
            
            # Try to extract JSON from the response
            content = response.content.strip()
            
            # If response is wrapped in markdown code blocks, extract it
            if content.startswith("```"):
                # Extract content between code blocks
                match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
                if match:
                    content = match.group(1)
            
            sub_questions = json.loads(content)
            
            # Ensure it's a list
            if not isinstance(sub_questions, list):
                sub_questions = [question]
            
            logger.info(f"Generated {len(sub_questions)} sub-questions")
            return sub_questions
            
        except Exception as e:
            logger.warning(f"Error in query decomposition: {str(e)}. Using original question.")
            # Fallback to original question
            return [question]
    
    def retrieve_with_multi_query(self, question: str) -> List[Document]:
        logger.info("Starting multi-query retrieval")
        
        # Generate query variations
        queries = self.translate_query(question)
        
        # Add original question
        if question not in queries:
            queries.insert(0, question)
        
        # Retrieve documents for each query
        all_docs = []
        seen_contents = set()
        
        for query in queries:
            docs = self.vector_db.similarity_search(query, k=TOP_K_RESULTS)
            
            # Deduplicate based on content
            for doc in docs:
                content_hash = hash(doc.page_content)
                if content_hash not in seen_contents:
                    seen_contents.add(content_hash)
                    all_docs.append(doc)
        
        logger.info(f"Retrieved {len(all_docs)} unique documents")
        
        # Limit to top results
        return all_docs[:TOP_K_RESULTS * 2]
    
    def retrieve_with_decomposition(self, question: str) -> List[Document]:
        logger.info("Starting decomposition-based retrieval")
        
        # Decompose question
        sub_questions = self.decompose_query(question)
        
        # Retrieve documents for each sub-question
        all_docs = []
        seen_contents = set()
        
        for sub_q in sub_questions:
            docs = self.vector_db.similarity_search(sub_q, k=TOP_K_RESULTS)
            
            # Deduplicate
            for doc in docs:
                content_hash = hash(doc.page_content)
                if content_hash not in seen_contents:
                    seen_contents.add(content_hash)
                    all_docs.append(doc)
        
        logger.info(f"Retrieved {len(all_docs)} unique documents")
        
        return all_docs[:TOP_K_RESULTS * 2]
    
    def retrieve_with_scores(self, question: str) -> List[tuple]:
        logger.info("Retrieving documents with scores")
        
        results = self.vector_db.similarity_search_with_score(
            question, 
            k=TOP_K_RESULTS
        )
        
        return results
    
    def hybrid_retrieve(self, question: str, use_decomposition: bool = False) -> Dict[str, Any]:
        logger.info("Starting hybrid retrieval")
        
        # Choose retrieval strategy based on question complexity
        if use_decomposition or len(question.split()) > 15:
            docs = self.retrieve_with_decomposition(question)
            strategy = "decomposition"
        else:
            docs = self.retrieve_with_multi_query(question)
            strategy = "multi-query"
        
        # Get scores for top documents
        scored_results = self.retrieve_with_scores(question)
        
        return {
            "documents": docs,
            "scored_results": scored_results,
            "strategy": strategy,
            "num_results": len(docs)
        }
