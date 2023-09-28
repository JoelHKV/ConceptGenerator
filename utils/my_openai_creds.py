def my_openai():
    import openai
    import os  # Import the 'os' module to access environment variables
    api_key = os.environ.get("OPENAI_API_KEY") # Access OpenAI API key from environment variable  
    if api_key is None:
        raise ValueError("OpenAI API key not found in environment variable")   
    openai.api_key = api_key # Set up OpenAI API key
    print("OpenAI API credentials have been set up successfully.")