from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model=os.getenv("GROQ_MODEL"),
    temperature=0.4,
    max_tokens=1024,
    max_retries=3,
    timeout=30,
    streaming=True
    )


response = llm.invoke("Hello, how are you?")
print(response)