import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


async def get_openrouter_response(user_message: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }
    system_message = {
        "role": "system",
        "content": """You are Elara, a helpful AI assistant. Your name is Elara.

IMPORTANT INSTRUCTIONS:
- Keep responses professional and concise
- Use clear, straightforward language
- If unsure, say "I don't have enough information to answer that"
- Never make up information or pretend to have capabilities you don't 
- Do not use any emojis in your responses
- Avoid markdown formatting (no **bold**, *italic*, etc.)
- Avoid unnecessary formatting or symbols"""
    }
    payload = {
        "model": "openai/gpt-5-chat",
        "messages": [
            system_message,
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    # Extract the AI's reply text
    return data["choices"][0]["message"]["content"]