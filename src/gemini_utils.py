import os
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_random, retry_if_exception_type
import google.generativeai as genai

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
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "❌ No se ha encontrado la API KEY. Añádela en los secretos de Streamlit o como variable de entorno."

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"temperature": temperature}
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error generando conclusión: {e}"

