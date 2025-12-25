"""Streamlit UI."""
import streamlit as st
import time
from chatbot import TechnicalDocAssistant
from logger import logger
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Python Docs Copilot",
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
        opacity: 0.8;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .user-message {
        background-color: rgba(33, 150, 243, 0.1);
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: rgba(76, 175, 80, 0.1);
        border-left-color: #4caf50;
    }
    .metadata {
        font-size: 0.85rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    .tool-call {
        background-color: rgba(255, 152, 0, 0.1);
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        border-left: 3px solid #ff9800;
    }
    .source-badge {
        display: inline-block;
        background-color: rgba(128, 128, 128, 0.2);
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem;
        font-size: 0.8rem;
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

    if 'visual_mode' not in st.session_state:
        st.session_state.visual_mode = False


def render_visual(visual: dict):
    if not isinstance(visual, dict):
        return

    chart_type = visual.get("type")
    title = visual.get("title")
    data = visual.get("data")
    x = visual.get("x")
    y = visual.get("y")

    if title:
        st.markdown(f"#### {title}")

    if not isinstance(data, dict):
        st.info("No visual data provided.")
        return

    columns = data.get("columns")
    rows = data.get("rows")
    if not isinstance(columns, list) or not isinstance(rows, list):
        st.info("Visual data was not in the expected format.")
        return

    try:
        df = pd.DataFrame(rows, columns=columns)
    except Exception:
        st.info("Could not render visual data.")
        return

    if chart_type == "table":
        st.dataframe(df, use_container_width=True)
        return

    if chart_type in {"bar", "line", "scatter"}:
        if x not in df.columns or y not in df.columns:
            st.dataframe(df, use_container_width=True)
            return

        df2 = df[[x, y]].copy()
        df2[y] = pd.to_numeric(df2[y], errors="coerce")

        if chart_type == "bar":
            st.bar_chart(df2.set_index(x)[y])
        elif chart_type == "line":
            st.line_chart(df2.set_index(x)[y])
        else:
            st.scatter_chart(df2, x=x, y=y)
        return

    st.dataframe(df, use_container_width=True)


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

        visual_mode = st.checkbox(
            "Enable Visual Answers",
            value=st.session_state.visual_mode,
            help="Allow the assistant to return a chart/table in addition to text"
        )
        st.session_state.visual_mode = visual_mode
        
        st.markdown("---")
        
        # Information
        st.markdown("### 📚 About")
        st.info("""
        **Python Docs Copilot**
        
        Ask questions about Python and get answers grounded in your indexed docs.
        
        **How it works:**
        - 🔎 Retrieves relevant snippets from a local knowledge base (RAG)
        - 🧠 Improves recall via query translation (and decomposition for longer questions)
        
        **Built-in tools:**
        - 🛠️ Execute Python snippets (restricted sandbox)
        - 📦 Look up package info & latest version from PyPI
        - 📖 Jump to official documentation links for supported libraries
        
        **Extras:**
        - 📈 Optional visual answers (tables / charts)
        """)
        
        st.markdown("---")
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        
        examples = [
            "Summarize how pandas.merge works and cite sources",
            "What's the latest version of fastapi on PyPI?",
            "Execute this code and explain the output: print(sum(range(10)))",
            "Find official docs for sqlalchemy relationships",
            "Show a table comparing numpy arrays vs Python lists",
            "Make a bar chart of these values: A=10, B=7, C=3"
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
    st.markdown('<div class="main-header">📚 Python Docs Copilot</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">RAG-powered answers with tools and visuals</div>', 
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

        if message["role"] == "assistant" and (message.get("visual_mode") or message.get("visual")):
            with st.expander("📈 Visual", expanded=True):
                if message.get("visual"):
                    render_visual(message.get("visual"))
                else:
                    st.info("No visual was returned for this answer. Ask explicitly for a chart/table (e.g., 'show a table' or 'make a bar chart').")
    
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
                    use_tools=st.session_state.use_tools,
                    visual_mode=st.session_state.visual_mode
                )
                
                response = result["response"]
                visual = result.get("visual")
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
                    "metadata": metadata,
                    "visual": visual,
                    "visual_mode": st.session_state.visual_mode
                })
                
                # Display assistant message
                display_message("assistant", response, metadata)

                if st.session_state.visual_mode or visual:
                    with st.expander("📈 Visual", expanded=True):
                        if visual:
                            render_visual(visual)
                        else:
                            st.info("No visual was returned for this answer. Ask explicitly for a chart/table (e.g., 'show a table' or 'make a bar chart').")
                
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
