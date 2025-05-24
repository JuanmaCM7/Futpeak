import streamlit as st
import google.generativeai as genai
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_random, retry_if_exception_type

# 🎯 Decorador para reintentos
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

@with_retry
def generar_conclusion_gemini(prompt: str, temperature: float = 0.3) -> str:
    api_key = st.secrets.get("GOOGLE_API_KEY")

    if not api_key:
        print("❌ No se encontró GOOGLE_API_KEY en st.secrets.")
        return "❌ No se encontró la API KEY en st.secrets."

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"temperature": temperature}
        )

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error al usar Gemini: {e}")
        return f"❌ Error generando conclusión: {e}"
