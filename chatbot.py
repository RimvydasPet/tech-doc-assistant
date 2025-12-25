import json
from typing import List, Dict, Any
import re
import math
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from vector_db import VectorDatabase
from rag_engine import AdvancedRAGEngine
from tools import CodeExecutor, PackageInfoFetcher, DocumentationSearcher
from logger import logger
from config import GOOGLE_API_KEY, GOOGLE_MODEL, MAX_TOKENS_PER_REQUEST, SUPPORTED_LIBRARIES


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
1. execute_code: Run Python code snippets safely (use for examples, testing, verification)
2. get_package_info: Get package information from PyPI (use for version/dependency questions)
3. search_documentation: Find official documentation links (use when users need official docs)

When tools are enabled, I will automatically detect when tools should be used and provide you with the results.
When tools are disabled, answer based only on the provided context and your knowledge.

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
- If tool results are provided, incorporate them naturally into your response

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
                # Check if user is trying to use tool features with tools disabled
                tool_warning = self._get_disabled_tools_warning(user_message)
                response = self.llm.invoke(messages)
                response = response.content
                if tool_warning:
                    response = f"{tool_warning}\n\n{response}"

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
    
    def _get_disabled_tools_warning(self, message: str) -> str:
        """Return a friendly warning if user tries to use tool features while tools are disabled."""
        message_lower = message.lower()
        
        # Check for code execution intent
        if any(kw in message_lower for kw in ["execute:", "run:", "code:", "print("]):
            return "⚠️ **Tool calling is disabled.** I cannot execute code right now. Enable tool calling to run Python code snippets."
        
        # Check for package info intent
        if any(kw in message_lower for kw in ["latest version", "pypi", "what version"]):
            return "⚠️ **Tool calling is disabled.** I cannot fetch live package info from PyPI. Enable tool calling to get real-time package data."
        
        # Check for documentation search intent
        if any(kw in message_lower for kw in ["official docs", "documentation link", "find docs"]):
            return "⚠️ **Tool calling is disabled.** I cannot search official documentation. Enable tool calling to get documentation links."
        
        return ""
    
    def _generate_with_tools(self, messages: List) -> str:
        """Generate response with automatic tool calling based on user intent."""
        logger.info("Generating response with tool calling capabilities")
        
        # Extract the user's message from conversation
        user_message = self._get_last_user_message(messages)
        
        # Detect which tools (if any) should be called
        tools_to_call = self._detect_tool_intent(user_message)
        
        # If no tools needed, generate a simple response
        if not tools_to_call:
            return self._generate_simple_response(messages)
        
        # Execute detected tools and get results
        tool_results = self._execute_tools(tools_to_call, user_message)
        
        # Generate response enhanced with tool results
        return self._generate_enhanced_response(messages, tool_results)
    
    def _get_last_user_message(self, messages: List) -> str:
        """Extract the last user message from the conversation."""
        for msg in reversed(messages):
            if hasattr(msg, 'content') and isinstance(msg.content, str):
                return msg.content
        return ""
    
    def _generate_simple_response(self, messages: List) -> str:
        """Generate a response without tool augmentation."""
        response = self.llm.invoke(messages)
        return response.content
    
    def _generate_enhanced_response(self, messages: List, tool_results: Dict[str, Any]) -> str:
        """Generate a response enhanced with tool execution results."""
        tool_context = self._format_tool_results(tool_results)
        enhanced_messages = messages + [
            SystemMessage(content=f"Tool Results:\n{tool_context}")
        ]
        response = self.llm.invoke(enhanced_messages)
        return response.content
    
    def _detect_tool_intent(self, message: str) -> List[str]:
        """Detect which tools should be called based on user message."""
        tools_needed = []
        message_lower = message.lower()
        
        # Code execution patterns
        if any(keyword in message_lower for keyword in [
            "execute:", "run:", "code:", "print(", "import ", "calculate", 
            "compute", "test", "try", "example", "show me", "demonstrate"
        ]):
            tools_needed.append("execute_code")
        
        # Package info patterns
        if any(keyword in message_lower for keyword in [
            "version", "latest", "package", "pypi", "install", "update", 
            "what's new", "release", "download", "dependencies"
        ]):
            tools_needed.append("get_package_info")
        
        # Documentation search patterns
        if any(keyword in message_lower for keyword in [
            "documentation", "docs", "official", "guide", "tutorial", 
            "reference", "manual", "help", "read more", "link"
        ]):
            tools_needed.append("search_documentation")
        
        return tools_needed
    
    def _execute_tools(self, tools_to_call: List[str], user_message: str) -> Dict[str, Any]:
        """Execute the detected tools."""
        results = {}
        
        for tool_name in tools_to_call:
            try:
                if tool_name == "execute_code":
                    # Extract code from message
                    code = self._extract_code_from_message(user_message)
                    if code:
                        results[tool_name] = self.tools["execute_code"]["func"](code)
                
                elif tool_name == "get_package_info":
                    # Extract package name from message
                    package_name = self._extract_package_name(user_message)
                    if package_name:
                        results[tool_name] = self.tools["get_package_info"]["func"](package_name)
                
                elif tool_name == "search_documentation":
                    # Extract library and query from message
                    library, query = self._extract_doc_search_params(user_message)
                    if library:
                        results[tool_name] = self.tools["search_documentation"]["func"](library, query)
                
            except Exception as e:
                logger.error(f"Error executing {tool_name}: {str(e)}")
                results[tool_name] = {"success": False, "error": str(e)}
        
        return results
    
    def _extract_code_from_message(self, message: str) -> str:
        """Extract Python code from user message."""
        import re
        
        # Look for code blocks
        code_block_match = re.search(r'```(?:python)?\s*(.*?)\s*```', message, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()
        
        # Look for execute: pattern
        execute_match = re.search(r'execute:\s*(.+?)(?:\n|$)', message, re.IGNORECASE)
        if execute_match:
            return execute_match.group(1).strip()
        
        # Look for run: pattern
        run_match = re.search(r'run:\s*(.+?)(?:\n|$)', message, re.IGNORECASE)
        if run_match:
            return run_match.group(1).strip()
        
        return ""
    
    def _extract_package_name(self, message: str) -> str:
        """Extract package name from user message."""
        import re
        
        # Look for common patterns
        for library in SUPPORTED_LIBRARIES:
            if library.lower() in message.lower():
                return library
        
        # Look for "package X" pattern
        package_match = re.search(r'package\s+(\w+)', message, re.IGNORECASE)
        if package_match:
            return package_match.group(1).lower()
        
        return ""
    
    def _extract_doc_search_params(self, message: str) -> tuple:
        """Extract library and query from documentation search request."""
        import re
        
        # Try to find library name
        library = None
        for lib in SUPPORTED_LIBRARIES:
            if lib.lower() in message.lower():
                library = lib
                break
        
        # Extract query (everything after library name or keywords)
        query = message
        if library:
            query = message.replace(library, "").strip()
        
        # Remove common prefixes
        for prefix in ["find", "search", "show", "get", "documentation", "docs"]:
            query = query.replace(prefix, "").strip()
        
        return library, query if query else "documentation"
    
    def _format_tool_results(self, tool_results: Dict[str, Any]) -> str:
        """Format tool results for inclusion in conversation context."""
        formatted = []
        
        for tool_name, result in tool_results.items():
            if tool_name == "execute_code":
                if result.get("success"):
                    formatted.append(f"Code Execution Result:\n{result.get('output', 'No output')}")
                else:
                    formatted.append(f"Code Execution Error: {result.get('error', 'Unknown error')}")
            
            elif tool_name == "get_package_info":
                if result.get("success"):
                    data = result.get("data", {})
                    formatted.append(f"Package Information:\n- Name: {data.get('name')}\n- Version: {data.get('version')}\n- Summary: {data.get('summary')}")
                else:
                    formatted.append(f"Package Info Error: {result.get('error', 'Unknown error')}")
            
            elif tool_name == "search_documentation":
                if result.get("success"):
                    results = result.get("results", [])
                    formatted.append(f"Documentation Links:\n" + "\n".join([f"- {r.get('title')}: {r.get('url')}" for r in results]))
                else:
                    formatted.append(f"Documentation Search Error: {result.get('error', 'Unknown error')}")
        
        return "\n\n".join(formatted)
    
    def clear_history(self) -> None:
        self.conversation_history = []
        logger.info("Conversation history cleared")
