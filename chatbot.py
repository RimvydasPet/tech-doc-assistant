import json
from typing import List, Dict, Any, Optional
import re
import math
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from vector_db import VectorDatabase
from rag_engine import AdvancedRAGEngine
from tools import CodeExecutor, PackageInfoFetcher, DocumentationSearcher
from logger import logger
from config import GOOGLE_API_KEY, GOOGLE_MODEL, MAX_TOKENS_PER_REQUEST


class TechnicalDocAssistant:
    
    def __init__(self):
        logger.info("Initializing Technical Documentation Assistant")
        
        # Vector database
        self.vector_db = VectorDatabase()
        self.vector_db.initialize()
        
        # RAG engine
        self.rag_engine = AdvancedRAGEngine(self.vector_db)
        
        # LLM
        self.llm = ChatGoogleGenerativeAI(
            model=GOOGLE_MODEL,
            temperature=0.7,
            max_output_tokens=MAX_TOKENS_PER_REQUEST,
            google_api_key=GOOGLE_API_KEY
        )
        
        # Tools and history
        self.tools = self._setup_tools()
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info("Chatbot initialized successfully")
    
    def _setup_tools(self) -> Dict[str, Any]:
        tools = {
            "execute_code": {
                "func": CodeExecutor.execute_code,
                "description": "Execute Python code in a safe environment"
            },
            "get_package_info": {
                "func": PackageInfoFetcher.get_package_info,
                "description": "Get information about a Python package from PyPI"
            },
            "search_documentation": {
                "func": DocumentationSearcher.search_docs,
                "description": "Search official documentation for a Python library"
            }
        }
        
        return tools
    
    def _create_system_prompt(self, context: str) -> str:
        return f"""You are a Technical Documentation Assistant specializing in Python libraries.
Your role is to help developers understand and work with Python libraries like pandas, numpy, 
scikit-learn, matplotlib, and others.

You have access to the following tools:
1. execute_code: Run Python code snippets safely
2. get_package_info: Get package information from PyPI
3. search_documentation: Find official documentation links

CONTEXT FROM KNOWLEDGE BASE:
{context}

GUIDELINES:
- Provide accurate, detailed explanations based on the context
- Use code examples to illustrate concepts
- When appropriate, use tools to demonstrate or verify information
- If you're unsure, say so and suggest where to find more information
- Always cite sources when using information from the context
- Be concise but thorough
- Format code using markdown code blocks
- If the user asks to run code, use the execute_code tool
- If the user asks about package versions or info, use get_package_info
- If the user needs documentation links, use search_documentation

Remember: You're helping developers learn and solve problems efficiently."""

    def _create_system_prompt_visual(self, context: str) -> str:
        return f"""You are a Technical Documentation Assistant specializing in Python libraries.
Your role is to help developers understand and work with Python libraries like pandas, numpy,
scikit-learn, matplotlib, and others.

You have access to the following tools:
1. execute_code: Run Python code snippets safely
2. get_package_info: Get package information from PyPI
3. search_documentation: Find official documentation links

CONTEXT FROM KNOWLEDGE BASE:
{context}

GUIDELINES:
- Provide accurate, detailed explanations based on the context
- Be concise but thorough
- Always cite sources when using information from the context
- Format code using markdown code blocks

VISUAL OUTPUT MODE:
- You MUST output a single valid JSON object (and nothing else).
- JSON schema:
  {{
    "response": "<markdown string>",
    "visual": null | {{
      "type": "table" | "bar" | "line" | "scatter",
      "title": "<short title>",
      "data": {{
        "columns": ["col1", "col2", ...],
        "rows": [[...], [...]]
      }},
      "x": "<column name>",
      "y": "<column name>"
    }}
  }}
- If the user asks for a chart/plot/visualization OR provides matplotlib/plt.* plotting code, you MUST include a non-null "visual".
- Otherwise, set "visual" to null.
- Keep tables small (<= 50 rows).

Remember: You're helping developers learn and solve problems efficiently."""
    
    def _format_context(self, documents: List) -> str:
        if not documents:
            return "No specific context found in knowledge base."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            source = metadata.get('source', 'unknown')
            category = metadata.get('category', 'general')
            
            context_parts.append(
                f"[Source {i}: {category}/{source}]\n{doc.page_content}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def chat(self, user_message: str, use_tools: bool = True, visual_mode: bool = False, **kwargs) -> Dict[str, Any]:
        logger.info(f"Processing user message: {user_message[:50]}...")
        
        try:
            # Retrieve relevant context using RAG
            retrieval_result = self.rag_engine.hybrid_retrieve(user_message)
            documents = retrieval_result["documents"]
            context = self._format_context(documents)
            
            # Create system prompt with context
            system_prompt = (
                self._create_system_prompt_visual(context)
                if visual_mode
                else self._create_system_prompt(context)
            )
            
            # Build conversation messages
            messages = [SystemMessage(content=system_prompt)]
            
            # Add conversation history
            for msg in self.conversation_history[-6:]:  # Last 3 exchanges
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add current message
            if visual_mode:
                plot_like = any(
                    token in user_message.lower()
                    for token in ["plt.", "matplotlib", "plot", "chart", "visual", "graph", "line plot", "bar chart", "scatter"]
                )
                if plot_like:
                    messages.append(
                        HumanMessage(
                            content=(
                                user_message
                                + "\n\nReturn the JSON with a non-null visual. "
                                + "If you need numbers, invent a small illustrative dataset and include it in visual.data."
                            )
                        )
                    )
                else:
                    messages.append(HumanMessage(content=user_message))
            else:
                messages.append(HumanMessage(content=user_message))
            
            # Generate response
            if use_tools:
                response = self._generate_with_tools(messages)
            else:
                response = self.llm.invoke(messages)
                response = response.content

            visual = None
            if visual_mode:
                parsed = None
                content = response.strip() if isinstance(response, str) else ""

                if content.startswith("```"):
                    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
                    if match:
                        content = match.group(1).strip()

                if not content.startswith("{"):
                    match = re.search(r"(\{.*\})", content, re.DOTALL)
                    if match:
                        content = match.group(1).strip()

                try:
                    parsed = json.loads(content)
                except Exception:
                    parsed = None

                if isinstance(parsed, dict):
                    response = parsed.get("response", response)
                    visual = parsed.get("visual")

                if visual is None:
                    lower_msg = user_message.lower()

                    list_match = re.search(r"\[\s*([0-9eE+\-\.,\s]+)\s*\]", user_message)
                    if list_match and ("sin" in lower_msg and "line" in lower_msg or "sin(x)" in lower_msg):
                        try:
                            xs = [float(x.strip()) for x in list_match.group(1).split(",") if x.strip()]
                            ys = [math.sin(x) for x in xs]
                            visual = {
                                "type": "line",
                                "title": "sin(x)",
                                "data": {
                                    "columns": ["x", "sin(x)"],
                                    "rows": [[x, y] for x, y in zip(xs[:50], ys[:50])],
                                },
                                "x": "x",
                                "y": "sin(x)",
                            }
                        except Exception:
                            visual = None

                    if visual is None and ("bar" in lower_msg or "bar chart" in lower_msg):
                        try:
                            pairs = re.findall(r"([A-Za-z0-9_\-]+)\s*=\s*([0-9]+(?:\.[0-9]+)?)", user_message)
                            if pairs:
                                visual = {
                                    "type": "bar",
                                    "title": "Bar chart",
                                    "data": {
                                        "columns": ["label", "value"],
                                        "rows": [[k, float(v)] for k, v in pairs[:50]],
                                    },
                                    "x": "label",
                                    "y": "value",
                                }
                        except Exception:
                            visual = None
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            logger.info("Response generated successfully")
            
            return {
                "response": response,
                "visual": visual,
                "context_used": len(documents),
                "retrieval_strategy": retrieval_result["strategy"],
                "sources": [doc.metadata for doc in documents if hasattr(doc, 'metadata')]
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "response": f"I encountered an error: {str(e)}. Please try rephrasing your question.",
                "visual": None,
                "context_used": 0,
                "retrieval_strategy": "none",
                "sources": []
            }
    
    def _generate_with_tools(self, messages: List) -> str:
        logger.info("Generating response (tool calling simplified for compatibility)")
        response = self.llm.invoke(messages)
        return response.content
    
    def clear_history(self) -> None:
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        return self.conversation_history
