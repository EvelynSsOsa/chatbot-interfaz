import os
import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from pdfminer.high_level import extract_text

# --- Modelo y embeddings
modelo_embeddings = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
modelo_lenguaje = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")

# --- Función para extraer texto desde PDF
def extraer_texto_de_pdf(nombre_pdf):
    ruta = os.path.join("pdfs_subidos", nombre_pdf)
    texto = extract_text(ruta)
    return texto

# --- Función principal
def responder_pregunta(pregunta, nombre_pdf):
    texto = extraer_texto_de_pdf(nombre_pdf)

    # Preprocesar texto
    texto = texto.replace("\n", " ").replace("  ", " ")
    fragmentos = [f.strip() for f in texto.split(". ") if len(f.strip()) > 30 and len(f.strip()) < 500]

    if not fragmentos:
        return "No se pudo encontrar información útil en el PDF."

    # Embeddings
    fragmentos_embeddings = modelo_embeddings.encode(fragmentos)
    embedding_pregunta = modelo_embeddings.encode([pregunta])[0]

    # Buscar el fragmento más relevante
    similitudes = np.dot(fragmentos_embeddings, embedding_pregunta)
    idx_mas_relevante = np.argmax(similitudes)
    contexto = fragmentos[idx_mas_relevante][:500]  # Limitar contexto

    # Crear prompt
    prompt = (
        f"Basado en el siguiente contexto, responde con precisión a la pregunta.\n\n"
        f"Contexto: {contexto}\n"
        f"Pregunta: {pregunta}\n"
        f"Respuesta:"
    )

    # Preparar entrada y generar respuesta
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    outputs = modelo_lenguaje.generate(**inputs, max_new_tokens=100)
    salida = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extraer solo la respuesta
    if "Respuesta:" in salida:
        respuesta = salida.split("Respuesta:")[-1].strip()
    else:
        respuesta = salida.strip()

    return respuesta if respuesta else "No encontré una respuesta clara en el documento."
