"""
Streamlit Chat UI for Library Desk Agent
"""
import streamlit as st
import requests
from typing import Dict

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
DEFAULT_SESSION_ID = "default-session"

# Page config
st.set_page_config(
    page_title="Library Desk Agent",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    [data-testid="collapsedControl"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def check_backend_health():
    """Check if backend is running (runs only once)"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


@st.cache_resource
def create_default_session():
    """Create default session in backend (runs only once)"""
    try:
        requests.post(
            f"{BACKEND_URL}/api/sessions/new",
            json={"session_id": DEFAULT_SESSION_ID},
            timeout=5
        )
        return True
    except:
        return False


def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "initialized" not in st.session_state:
        create_default_session()
        st.session_state.initialized = True


def send_message(message: str) -> Dict:
    """Send message to agent and get response"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={"session_id": DEFAULT_SESSION_ID, "message": message},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "message": f"Error: {response.status_code}",
                "error": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection error: {str(e)}",
            "error": str(e)
        }




def render_chat():
    """Render the main chat interface"""
    
    # Header with title and clear button
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("📚 Library Desk Agent")
    with col2:
        if st.button("🗑️", help="Clear chat history", key="clear_btn"):
            st.session_state.messages = []
    
    st.markdown("---")
    
    # Show welcome message if no messages yet
    if len(st.session_state.messages) == 0:
        st.markdown("""
        ### 👋 Welcome to the Library Desk Agent!
        
        I'm an AI assistant that can help you manage library operations:
        
        **What I can do:**
        - 📖 **Search books** by title or author
        - 🛒 **Create orders** for customers
        - 📦 **Restock inventory** 
        - 💰 **Update prices**
        - 📊 **View inventory status** and low stock items
        
        **Try these examples:**
        - "Find books by Robert Martin"
        - "Create an order for customer 2: 1 copy of Clean Code"
        - "What's the status of order 1?"
        - "Show me books with low stock"
        - "Restock The Pragmatic Programmer by 10 copies"
        
        ---
        
        Ask me anything about the library below! 👇
        """)
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        elif role == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(content)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about the library..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Display assistant response with spinner
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = send_message(prompt)
                
                if response.get("success", False):
                    assistant_message = response.get("message", "")
                    st.markdown(assistant_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_message
                    })
                else:
                    error_msg = response.get("message", "An error occurred")
                    st.error(error_msg)
                    if "error" in response:
                        with st.expander("Error details"):
                            st.code(response["error"])


def main():
    """Main application"""
    init_session_state()
    render_chat()


if __name__ == "__main__":
    # Check backend health once (cached)
    if not check_backend_health():
        st.error("""
        ⚠️ **Backend server is not running!**
        
        Please start the backend server first:
        ```bash
        python server/main.py
        ```
        
        Then refresh this page.
        """)
        # Add button to retry
        if st.button("🔄 Retry Connection"):
            check_backend_health.clear()
            st.rerun()
        st.stop()
    
    main()

