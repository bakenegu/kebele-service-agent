import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()

# Get OpenAI API key from environment (works with Hugging Face Spaces secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

# Gradio settings
GRADIO_SHARE = os.getenv("GRADIO_SHARE", "False") == "True"  # Default False for HF Spaces
GRADIO_SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not set. "
        "For local: Put it in .env file. "
        "For Hugging Face Spaces: Add it as a secret in Space settings."
    )
