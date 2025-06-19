# text_processor.py

# pip install sentence-transformers torch

from sentence_transformers import SentenceTransformer
import numpy as np

# Cargar el modelo una sola vez
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def procesar_texto_en_chunks(texto: str):
    """
    Divide un texto en párrafos, genera embeddings y retorna una lista de diccionarios.
    Cada diccionario tiene 'text' y 'embedding'.
    """
    # Dividir el texto en párrafos
    paragraphs = [p.strip() for p in texto.split('\n\n') if p.strip()]

    # Generar embeddings para cada párrafo
    chunks_with_embeddings = []
    for paragraph in paragraphs:
        cleaned_paragraph = paragraph.replace('\n', ' ').replace('  ', ' ')
        embedding = model.encode(cleaned_paragraph)
        chunks_with_embeddings.append({
            'text': paragraph,
            'embedding': embedding
        })

    return chunks_with_embeddings
