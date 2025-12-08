"""Streamlit UI."""
import streamlit as st
import time
from datetime import datetime
from chatbot import TechnicalDocAssistant
from logger import logger
import json

# Page configuration
st.set_page_config(
    page_title="Technical Documentation Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with proper contrast for both light and dark themes
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
        color: #000 !important;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
        color: #000 !important;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left-color: #4caf50;
        color: #000 !important;
    }
    .chat-message * {
        color: #000 !important;
    }
    .metadata {
        font-size: 0.85rem;
        color: #555 !important;
        margin-top: 0.5rem;
    }
    .tool-call {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        border-left: 3px solid #ff9800;
        color: #000 !important;
    }
    .source-badge {
        display: inline-block;
        background-color: #e0e0e0;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem;
        font-size: 0.8rem;
        color: #000 !important;
    }
    /* Ensure all text in main content is visible */
    .main .block-container {
        color: inherit;
    }
    /* Fix for dark theme */
    [data-testid="stMarkdownContainer"] {
        color: inherit;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    if 'chatbot' not in st.session_state:
        with st.spinner("🔧 Initializing chatbot... This may take a moment."):
            try:
                st.session_state.chatbot = TechnicalDocAssistant()
                st.session_state.initialized = True
                logger.info("Chatbot initialized in session state")
            except Exception as e:
                st.error(f"Failed to initialize chatbot: {str(e)}")
                st.session_state.initialized = False
                logger.error(f"Initialization error: {str(e)}")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'use_tools' not in st.session_state:
        st.session_state.use_tools = True


def display_message(role: str, content: str, metadata: dict = None):
    css_class = "user-message" if role == "user" else "assistant-message"
    icon = "👤" if role == "user" else "🤖"
    
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <strong>{icon} {role.title()}</strong><br/>
        {content}
    </div>
    """, unsafe_allow_html=True)
    
    # Display metadata for assistant messages
    if role == "assistant" and metadata:
        with st.expander("📊 Response Metadata", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Context Documents", metadata.get("context_used", 0))
            
            with col2:
                st.metric("Retrieval Strategy", metadata.get("retrieval_strategy", "N/A"))
            
            with col3:
                st.metric("Sources", len(metadata.get("sources", [])))
            
            # Display sources
            if metadata.get("sources"):
                st.write("**Sources Used:**")
                for source in metadata["sources"]:
                    category = source.get("category", "unknown")
                    source_name = source.get("source", "unknown")
                    st.markdown(f'<span class="source-badge">{category}/{source_name}</span>', 
                              unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Tool usage toggle
        use_tools = st.checkbox(
            "Enable Tool Calling",
            value=st.session_state.use_tools,
            help="Allow the assistant to execute code, fetch package info, and search documentation"
        )
        st.session_state.use_tools = use_tools
        
        st.markdown("---")
        
        # Information
        st.markdown("### 📚 About")
        st.info("""
        **Technical Documentation Assistant**
        
        This AI assistant helps you understand and work with Python libraries.
        
        **Capabilities:**
        - 🔍 Advanced RAG with query translation
        - 🛠️ Code execution
        - 📦 Package information lookup
        - 📖 Documentation search
        
        **Supported Libraries:**
        - pandas, numpy, scikit-learn
        - matplotlib, seaborn
        - requests, flask, django
        - fastapi, sqlalchemy
        """)
        
        st.markdown("---")
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        
        examples = [
            "How do I create a pandas DataFrame?",
            "Show me how to use numpy arrays",
            "What's the latest version of scikit-learn?",
            "Execute this code: print('Hello, World!')",
            "Find documentation for matplotlib plotting"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{hash(example)}"):
                st.session_state.example_query = example
        
        st.markdown("---")
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            if hasattr(st.session_state, 'chatbot'):
                st.session_state.chatbot.clear_history()
            st.rerun()
        
        # Statistics
        st.markdown("---")
        st.markdown("### 📊 Statistics")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Conversations", len(st.session_state.messages) // 2)


def main():
    # Initialize
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">📚 Technical Documentation Assistant</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your AI-powered guide to Python libraries</div>', 
                unsafe_allow_html=True)
    
    # Sidebar
    sidebar()
    
    # Check if initialized
    if not st.session_state.get('initialized', False):
        st.error("⚠️ Chatbot failed to initialize. Please check your configuration and API key.")
        st.stop()
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(
            message["role"],
            message["content"],
            message.get("metadata")
        )
    
    # Handle example query
    if hasattr(st.session_state, 'example_query'):
        user_input = st.session_state.example_query
        delattr(st.session_state, 'example_query')
    else:
        user_input = None
    
    # Chat input
    if prompt := (user_input or st.chat_input("Ask me anything about Python libraries...")):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        display_message("user", prompt)
        
        # Generate response
        with st.spinner("🤔 Thinking..."):
            try:
                start_time = time.time()
                
                # Get response from chatbot
                result = st.session_state.chatbot.chat(
                    prompt,
                    use_tools=st.session_state.use_tools
                )
                
                response = result["response"]
                metadata = {
                    "context_used": result.get("context_used", 0),
                    "retrieval_strategy": result.get("retrieval_strategy", "none"),
                    "sources": result.get("sources", []),
                    "response_time": round(time.time() - start_time, 2)
                }
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "metadata": metadata
                })
                
                # Display assistant message
                display_message("assistant", response, metadata)
                
                logger.info(f"Response generated in {metadata['response_time']}s")
                
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                logger.error(f"Error in chat: {str(e)}")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
        
        # Rerun to update the display
        st.rerun()


if __name__ == "__main__":
    main()
