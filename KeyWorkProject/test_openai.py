# test_openai.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key (primeros 10 caracteres): {api_key[:10]}...")

client = OpenAI(api_key=api_key)

try:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="Texto de prueba para embedding"
    )
    print("¡Éxito! Embedding generado correctamente.")
    print(f"Dimensiones: {len(response.data[0].embedding)}")
except Exception as e:
    print(f"Error: {str(e)}")