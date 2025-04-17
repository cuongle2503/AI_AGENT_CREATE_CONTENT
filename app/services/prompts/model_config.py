"""
Configuration for AI models used in the application.
"""

# OpenAI models configuration
OPENAI_MODELS = {
    "gpt-4o": {
        "name": "GPT-4o",
        "description": "Powerful multimodal model with image analysis capabilities"
    },
    "gpt-4.1": {
        "name": "GPT-4.1",
        "description": "Advanced model with strong reasoning capabilities"
    },
    "gpt-4.1-mini": {
        "name": "GPT-4.1 Mini",
        "description": "Faster and more efficient version of GPT-4.1"
    }
}

# Default OpenAI model
DEFAULT_OPENAI_MODEL = "gpt-4o"

# Ollama models configuration
OLLAMA_MODELS = {
    "llama3.2": {
        "name": "LLaMA 3.2",
        "description": "Efficient open-source LLM for text enhancement"
    }
}

# Default Ollama model
DEFAULT_OLLAMA_MODEL = "llama3.2" 