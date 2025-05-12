# utils/openai_utils.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Función para generar embeddings
def get_embedding(text):
    if not text or text.strip() == "":
        print("Error: Texto vacío para embedding")
        return None
    
    try:
        print(f"Solicitando embedding para texto de {len(text)} caracteres")
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        embedding = response.data[0].embedding
        print(f"Embedding generado correctamente: {len(embedding)} dimensiones")
        return embedding
    except Exception as e:
        print(f"Error generando embedding: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Función para calcular similitud (usando la fórmula del coseno)
def calculate_similarity(embedding1, embedding2):
    import numpy as np
    
    if embedding1 is None or embedding2 is None:
        return 0
    
    # Convertir a arrays numpy
    vector1 = np.array(embedding1)
    vector2 = np.array(embedding2)
    
    # Calcular similitud del coseno
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    
    if norm1 == 0 or norm2 == 0:
        return 0
    
    return dot_product /(norm1 * norm2)