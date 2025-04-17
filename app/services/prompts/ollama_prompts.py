"""
Ollama model prompts for improving product descriptions.
"""

SYSTEM_MESSAGE = """You are a highly skilled SEO content specialist and creative writer. 
Your goal is to take the provided demo and improve it in terms of SEO, 
creativity, readability, and emotional appeal."""

USER_MESSAGE_TEMPLATE = """Please improve, enrich, and optimize my demo for SEO. 
The current demo is as follows: {openai_response}.""" 