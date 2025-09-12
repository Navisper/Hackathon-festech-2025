# app/ai_service.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek")  # usa tu modelo gratuito

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

async def get_ai_response(messages: list) -> str:
    """Llamada a OpenRouter para obtener respuesta de la IA"""
    # agregamos instrucción para que la IA sea breve
    short_prompt = {
        "role": "system",
        "content": "Responde de manera clara, breve y concisa. No te extiendas innecesariamente."
    }
    messages_with_short = [short_prompt] + messages

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages_with_short,
            max_tokens=250
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_str = str(e)
        if "402" in error_str:
            return (
                "Error: Créditos insuficientes para esta petición. "
                "Reduce la longitud del mensaje o usa otro modelo."
            )
        return f"Error llamando a la IA: {error_str}"