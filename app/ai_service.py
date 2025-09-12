# app/ai_service.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

async def get_ai_response(messages: list) -> str:
    """Llamada a OpenRouter para obtener respuesta de la IA"""
    try:
        response = client.chat.completions.create(
            model="openrouter/auto",  # o cambia a "gpt-4o-mini", "mistral" etc
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error llamando a la IA: {str(e)}"