import os
from pathlib import Path
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random, retry_if_exception_type
import google.generativeai as genai
from functools import wraps

def load_api_key() -> str:
    # Intenta detectar si __file__ está definido (no existe en notebooks)
    try:
        dotenv_path = Path(__file__).resolve().parents[1] / ".env"
    except NameError:
        # Estás en un notebook, ajusta la ruta manualmente
        dotenv_path = Path("../.env").resolve()

    load_dotenv(dotenv_path)
    return os.getenv("GOOGLE_API_KEY")

# 🎯 Decorador con retry que conserva los argumentos
def with_retry(func):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=1, max=2),
        retry=retry_if_exception_type(Exception)
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# 🎯 Función principal para generar conclusión
@with_retry
def generar_conclusion_gemini(prompt: str, temperature: float = 0.3) -> str:
    api_key = load_api_key()
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="models/gemini-1.5-flash",  # ¡Este sí funciona con tu API key!
        generation_config={"temperature": temperature}
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error generando conclusión: {e}"
