"""
LangChain Agent Setup
"""
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

from server.agent.tools import ALL_TOOLS

# Load environment variables
load_dotenv()


def load_system_prompt() -> str:
    """Load system prompt from file"""
    prompt_path = "./prompts/system_prompt.txt"
    try:
        with open(prompt_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return """You are a helpful Library Desk Agent assistant. 
        Help manage library operations including book inventory, customer orders, and information queries."""


def create_agent() -> AgentExecutor:
    """Create and configure the LangChain agent"""
    
    # Initialize LLM
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please set it in your .env file"
        )
    
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        api_key=api_key
    )
    
    # Load system prompt
    system_prompt = load_system_prompt()
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent
    agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return agent_executor


def format_chat_history(messages: List[Dict[str, str]]) -> List[Any]:
    """Convert message dicts to LangChain message objects"""
    chat_history = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        
        if role == "user":
            chat_history.append(HumanMessage(content=content))
        elif role == "assistant":
            chat_history.append(AIMessage(content=content))
        elif role == "system":
            chat_history.append(SystemMessage(content=content))
    
    return chat_history


async def run_agent(user_message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Run the agent with user input and chat history
    
    Args:
        user_message: User's input message
        chat_history: Previous messages in the conversation
    
    Returns:
        Dict with agent response and metadata
    """
    try:
        agent_executor = create_agent()
        
        # Format chat history
        formatted_history = []
        if chat_history:
            formatted_history = format_chat_history(chat_history)
        
        # Run agent
        result = await agent_executor.ainvoke({
            "input": user_message,
            "chat_history": formatted_history
        })
        
        return {
            "success": True,
            "output": result.get("output", ""),
            "intermediate_steps": result.get("intermediate_steps", [])
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output": f"I encountered an error: {str(e)}"
        }

