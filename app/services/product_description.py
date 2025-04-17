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

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    """Encode an image file to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_product_description(image_path, request_text=""):
    """Generate a product description based on an image and optional text."""
    try:
        # Encode the image to base64
        base64_image = encode_image(image_path)
        
        # Create chat completion request to OpenAI
        chat_completion = client.chat.completions.create(
            model="gpt-4o",  # Make sure the model name is correct
            messages=[
                {
                    "role": "system",
                    "content": OPENAI_SYSTEM_MESSAGE
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": OPENAI_USER_TEMPLATE.format(request_text=request_text)
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )

        # Extract OpenAI response
        openai_response = chat_completion.choices[0].message.content
        
        # Now send this OpenAI response to Ollama to improve the description
        improved_description = ollama.chat(
            model="llama3.2",  # Use Ollama model to improve the response
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