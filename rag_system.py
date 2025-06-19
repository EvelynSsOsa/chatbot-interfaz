# rag_system.py

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
    fragmentos = [f.strip() for f in texto.split(". ") if 30 < len(f.strip()) < 400]

    if not fragmentos:
        return "No se pudo encontrar información útil en el PDF."

    # Embeddings
    fragmentos_embeddings = modelo_embeddings.encode(fragmentos)
    embedding_pregunta = modelo_embeddings.encode([pregunta])[0]

    # Buscar el fragmento más relevante
    similitudes = np.dot(fragmentos_embeddings, embedding_pregunta)
    idx_mas_relevante = np.argmax(similitudes)
    contexto = fragmentos[idx_mas_relevante][:400]

    # Crear prompt sin repetir la pregunta y más claro para gpt-neo
    prompt = f"Contexto: {contexto}\n\nResponde de forma clara y precisa a esta pregunta:\n{pregunta}\n\nRespuesta:"

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    outputs = modelo_lenguaje.generate(**inputs, max_new_tokens=100, pad_token_id=tokenizer.eos_token_id)
    salida = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extraer solo la respuesta generada
    respuesta = salida.replace(prompt, "").strip()

    # En caso de que la respuesta esté vacía o poco clara
    if not respuesta or respuesta.lower() in prompt.lower():
        return "Lo siento, no encontré una respuesta clara en el PDF."

    return respuesta
