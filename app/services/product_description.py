import base64
import os
from openai import OpenAI
import ollama
from dotenv import load_dotenv

# Import prompt templates
from app.services.prompts.openai_prompts import SYSTEM_MESSAGE as OPENAI_SYSTEM_MESSAGE
from app.services.prompts.openai_prompts import USER_MESSAGE_TEMPLATE as OPENAI_USER_TEMPLATE
from app.services.prompts.ollama_prompts import SYSTEM_MESSAGE as OLLAMA_SYSTEM_MESSAGE
from app.services.prompts.ollama_prompts import USER_MESSAGE_TEMPLATE as OLLAMA_USER_TEMPLATE
from app.services.prompts.model_config import DEFAULT_OPENAI_MODEL, DEFAULT_OLLAMA_MODEL, OPENAI_MODELS, OLLAMA_MODELS

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    """Encode an image file to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_product_description(image_path, request_text="", openai_model=None, ollama_model=None):
    """
    Generate a product description based on an image and optional text.
    
    Args:
        image_path (str): Path to the product image
        request_text (str): Additional description or request text
        openai_model (str): OpenAI model to use for initial description
        ollama_model (str): Ollama model to use for enhancing the description
        
    Returns:
        str: The generated product description
    """
    return generate_product_description_multiple([image_path], request_text, openai_model, ollama_model)

def generate_product_description_multiple(image_paths, request_text="", openai_model=None, ollama_model=None):
    """
    Generate a product description based on multiple images and optional text.
    
    Args:
        image_paths (list): List of paths to product images
        request_text (str): Additional description or request text
        openai_model (str): OpenAI model to use for initial description
        ollama_model (str): Ollama model to use for enhancing the description
        
    Returns:
        str: The generated product description
    """
    try:
        # Use default models if none specified
        if not openai_model or openai_model not in OPENAI_MODELS:
            openai_model = DEFAULT_OPENAI_MODEL
            
        if not ollama_model or ollama_model not in OLLAMA_MODELS:
            ollama_model = DEFAULT_OLLAMA_MODEL
            
        # Prepare message content with user text
        message_content = [
            {
                "type": "text",
                "text": OPENAI_USER_TEMPLATE.format(request_text=request_text)
            }
        ]
        
        # Add all images to the message content
        for image_path in image_paths:
            base64_image = encode_image(image_path)
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpg;base64,{base64_image}"
                }
            })
        
        # Create chat completion request to OpenAI
        chat_completion = client.chat.completions.create(
            model=openai_model,
            messages=[
                {
                    "role": "system",
                    "content": OPENAI_SYSTEM_MESSAGE
                },
                {
                    "role": "user",
                    "content": message_content
                }
            ]
        )

        # Extract OpenAI response
        openai_response = chat_completion.choices[0].message.content
        
        # Now send this OpenAI response to Ollama to improve the description
        improved_description = ollama.chat(
            model=ollama_model,
            messages=[
                {
                    "role": "system",
                    "content": OLLAMA_SYSTEM_MESSAGE
                },
                {
                    "role": "user", 
                    "content": OLLAMA_USER_TEMPLATE.format(openai_response=openai_response)
                }
            ]
        )

        # Return the improved product description
        return improved_description['message']['content']

    except Exception as e:
        return f"An error occurred: {e}" 