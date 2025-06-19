
  # rag_system.py

import os
import faiss
import numpy as np
import torch
import pickle
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
    
    # Dividir en fragmentos
    fragmentos = texto.split(". ")
    fragmentos_embeddings = modelo_embeddings.encode(fragmentos)

    # Embedding de la pregunta
    embedding_pregunta = modelo_embeddings.encode([pregunta])[0]

    # Similitud
    similitudes = np.dot(fragmentos_embeddings, embedding_pregunta)
    idx_mas_relevante = np.argmax(similitudes)
    contexto = fragmentos[idx_mas_relevante]

    # Construir prompt y responder
    prompt = f"Contexto: {contexto}\nPregunta: {pregunta}\nRespuesta:"
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = modelo_lenguaje.generate(**inputs, max_new_tokens=100)
    respuesta = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return respuesta.replace(prompt, "").strip()
