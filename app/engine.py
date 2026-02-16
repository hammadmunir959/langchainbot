import os
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from .knowledge import SYSTEM_PROMPT
from .config import get_session_history

# Initialize LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model=os.getenv("GROQ_MODEL"),
    temperature=0.2,
    max_tokens=1024,
    max_retries=3,
    timeout=30,
    streaming=True
    )

# Define the core chain
base_chain = SYSTEM_PROMPT | llm | StrOutputParser()

# print(base_chain.invoke(

# ))


# full Wraped with history management
full_chain = RunnableWithMessageHistory(
    base_chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

def stream_response(
    input_text: str, 
    session_id: str, 
    user_name: str = "guest", 
    location: str = "unknown"
):
    """Streams response chunks from the LLM"""

    input_data = {
        "input": input_text, 
        "user_name": user_name, 
        "location": location or "unknown"
    }
    
    config = {
        "configurable": {
            "session_id": session_id
        }
    }
    
    yield from full_chain.stream(input_data, config=config)


# 2nd Endpoits

def get_history(session_id: str):
    """Retrieves list of messages for a get session endpoint."""

    history = get_session_history(session_id)

    return [
        {
            "role": "human" if msg.type == "human" else "ai", 
            "content": msg.content
        }   
        for msg in history.messages
    ]

