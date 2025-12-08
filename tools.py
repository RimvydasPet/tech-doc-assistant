"""Tool implementations for the chatbot."""
import subprocess
import sys
import json
import requests
from typing import Dict, Any, Optional
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import guarded_iter_unpack_sequence, safe_builtins
from io import StringIO
import contextlib
from logger import logger
from config import CODE_EXECUTION_TIMEOUT, MAX_CODE_LENGTH, SUPPORTED_LIBRARIES


class CodeExecutor:
    """Tool for safely executing Python code snippets."""
    
    @staticmethod
    def execute_code(code: str) -> Dict[str, Any]:
        """
        Execute Python code in a restricted environment.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dictionary with execution results and output
        """
        logger.info(f"Executing code snippet (length: {len(code)})")
        
        # Validate code length
        if len(code) > MAX_CODE_LENGTH:
            return {
                "success": False,
                "error": f"Code too long. Maximum {MAX_CODE_LENGTH} characters allowed.",
                "output": ""
            }
        
        # Capture stdout
        output_buffer = StringIO()
        
        try:
            # Compile with RestrictedPython
            byte_code = compile_restricted(
                code,
                filename='<inline code>',
                mode='exec'
            )
            
            if byte_code.errors:
                return {
                    "success": False,
                    "error": f"Compilation errors: {', '.join(byte_code.errors)}",
                    "output": ""
                }
            
            # Set up safe execution environment
            safe_globals_dict = {
                '__builtins__': safe_builtins,
                '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
                '_getiter_': lambda x: iter(x),
                'print': lambda *args, **kwargs: print(*args, **kwargs, file=output_buffer),
            }
            
            # Allow common safe libraries
            import math
            import random
            import datetime
            safe_globals_dict.update({
                'math': math,
                'random': random,
                'datetime': datetime,
            })
            
            # Execute the code
            with contextlib.redirect_stdout(output_buffer):
                exec(byte_code.code, safe_globals_dict)
            
            output = output_buffer.getvalue()
            logger.info("Code executed successfully")
            
            return {
                "success": True,
                "error": None,
                "output": output if output else "Code executed successfully (no output)"
            }
            
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output": output_buffer.getvalue()
            }


class PackageInfoFetcher:
    """Tool for fetching Python package information from PyPI."""
    
    @staticmethod
    def get_package_info(package_name: str) -> Dict[str, Any]:
        """
        Fetch package information from PyPI.
        
        Args:
            package_name: Name of the Python package
            
        Returns:
            Dictionary with package information
        """
        logger.info(f"Fetching package info for: {package_name}")
        
        try:
            # Query PyPI API
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Package '{package_name}' not found on PyPI",
                    "data": None
                }
            
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            info = data.get("info", {})
            releases = data.get("releases", {})
            
            # Get latest version
            latest_version = info.get("version", "Unknown")
            
            # Get release dates
            version_list = sorted(releases.keys(), reverse=True)[:5]
            
            result = {
                "success": True,
                "error": None,
                "data": {
                    "name": info.get("name", package_name),
                    "version": latest_version,
                    "summary": info.get("summary", "No summary available"),
                    "author": info.get("author", "Unknown"),
                    "license": info.get("license", "Unknown"),
                    "home_page": info.get("home_page", ""),
                    "project_urls": info.get("project_urls", {}),
                    "requires_python": info.get("requires_python", "Not specified"),
                    "recent_versions": version_list,
                }
            }
            
            logger.info(f"Successfully fetched info for {package_name}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error fetching package info: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to fetch package info: {str(e)}",
                "data": None
            }


class DocumentationSearcher:
    """Tool for searching official Python documentation."""
    
    @staticmethod
    def search_docs(library: str, query: str) -> Dict[str, Any]:
        """
        Search official documentation for a library.
        
        Args:
            library: Name of the library (e.g., 'pandas', 'numpy')
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        logger.info(f"Searching {library} docs for: {query}")
        
        if library.lower() not in [lib.lower() for lib in SUPPORTED_LIBRARIES]:
            return {
                "success": False,
                "error": f"Library '{library}' not in supported list: {', '.join(SUPPORTED_LIBRARIES)}",
                "results": []
            }
        
        # Documentation URLs for supported libraries
        doc_urls = {
            "pandas": "https://pandas.pydata.org/docs/",
            "numpy": "https://numpy.org/doc/stable/",
            "scikit-learn": "https://scikit-learn.org/stable/",
            "matplotlib": "https://matplotlib.org/stable/",
            "seaborn": "https://seaborn.pydata.org/",
            "requests": "https://requests.readthedocs.io/",
            "flask": "https://flask.palletsprojects.com/",
            "django": "https://docs.djangoproject.com/",
            "fastapi": "https://fastapi.tiangolo.com/",
            "sqlalchemy": "https://docs.sqlalchemy.org/",
        }
        
        base_url = doc_urls.get(library.lower())
        
        if not base_url:
            return {
                "success": False,
                "error": f"Documentation URL not configured for {library}",
                "results": []
            }
        
        try:
            # For this implementation, we'll return the base URL and suggest specific sections
            # In a production system, you'd implement actual doc scraping or use a search API
            
            result = {
                "success": True,
                "error": None,
                "results": [
                    {
                        "title": f"{library.title()} Official Documentation",
                        "url": base_url,
                        "description": f"Official documentation for {library}. Search for '{query}' in the documentation."
                    }
                ]
            }
            
            # Add common sections based on query keywords
            if "install" in query.lower():
                result["results"].append({
                    "title": "Installation Guide",
                    "url": f"{base_url}getting_started/install.html",
                    "description": "Installation instructions and requirements"
                })
            
            if "tutorial" in query.lower() or "guide" in query.lower():
                result["results"].append({
                    "title": "User Guide",
                    "url": f"{base_url}user_guide/",
                    "description": "Comprehensive user guide and tutorials"
                })
            
            if "api" in query.lower() or "reference" in query.lower():
                result["results"].append({
                    "title": "API Reference",
                    "url": f"{base_url}reference/",
                    "description": "Complete API reference documentation"
                })
            
            logger.info(f"Found {len(result['results'])} documentation links")
            return result
            
        except Exception as e:
            logger.error(f"Error searching documentation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }


# Tool registry for LangChain
TOOLS = {
    "execute_code": CodeExecutor.execute_code,
    "get_package_info": PackageInfoFetcher.get_package_info,
    "search_docs": DocumentationSearcher.search_docs,
}
