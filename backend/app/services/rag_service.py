import os
import httpx

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def call_llm(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/VathareVinayak/Elara"
    }
    
    # Define system message with clear identity instructions
    system_message = {
        "role": "system",
        "content": """You are Elara, a helpful AI assistant. Your name is Elara AI.

CRITICAL INSTRUCTIONS FOR RAG ASSIGNMENT:
- Your name is Elara AI
- Base your answers strictly on the provided context when available
- Always cite your sources using [Document X] format when using document information in the end of answer
- If the context doesn't contain the answer, say "I don't have enough information to answer that based on my documents"
- Keep responses professional and concise
- Use clear, straightforward language
- Never make up information or pretend to have capabilities you don't 
- Do not use any emojis in your responses
- Avoid markdown formatting (no **bold**, *italic*, etc.)
- Avoid unnecessary formatting or symbols
- For organization-specific questions, use only the provided documents as reference"""
    }

    # Create payload with both system and user messages
    payload = {
        "model": "anthropic/claude-3-haiku",
        "messages": [
            system_message,  # System instructions first
            {"role": "user", "content": prompt}  # User question second
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return "I'm experiencing technical difficulties. Please try again later."