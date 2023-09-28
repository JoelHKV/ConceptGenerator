import os

def get_openai_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("OpenAI API key not found in environment variable")
    return api_key