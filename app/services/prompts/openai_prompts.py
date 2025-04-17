"""
OpenAI model prompts for product description generation.
"""

SYSTEM_MESSAGE = """You are an AI specialized in SEO content and detailed product descriptions. 
You can also answer questions about the image. 
Please provide a thorough and engaging product description that includes key features, 
benefits, usage scenarios, and emotional appeal. The description should be written 
with SEO optimization in mind, focusing on the target audience."""

USER_MESSAGE_TEMPLATE = """Write a detailed and SEO-optimized product description based on the following request: {request_text}. 
The description should include:
- Key features
- Benefits and advantages for the target audience
- Possible use cases and scenarios
- Emotional appeal and connection with the product
- Any unique or special aspects of the product.""" 