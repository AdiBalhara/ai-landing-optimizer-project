from langchain_groq import ChatGroq
import os

def get_llm():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable not set. "
            "Get a free key at https://console.groq.com and add it to your Streamlit secrets."
        )
    return ChatGroq(
        model="llama3-8b-8192",  # free & fast on Groq's free tier
        api_key=api_key,
    )