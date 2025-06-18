# rag_system.py
# Este script ahora funciona con cualquier PDF que se haya subido recientemente a /pdfs_subidos

import os
import faiss
import numpy as np
import torch
import pickle
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from text_processor import procesar_texto_en_chunks
from pdf_extractor import extraer_texto_de_pdf

# --- Inicializar modelo de embeddings (una sola vez) ---
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# --- Inicializar modelo generativo (una sola vez) ---
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
modelo_llm = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")
generator = pipeline(
    "text-generation",
    model=modelo_llm,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1
)

# --- Obtener el último PDF subido ---
def obtener_ultimo_pdf():
    carpeta = "pdfs_subidos"
    archivos = [f for f in os.listdir(carpeta) if f.endswith(".pdf")]
    if not archivos:
        return None
    archivos.sort(key=lambda f: os.path.getmtime(os.path.join(carpeta, f)), reverse=True)
    return os.path.join(carpeta, archivos[0])

# --- Preparar índice FAISS dinámico ---
def construir_indice_desde_pdf(pdf_path):
    texto = extraer_texto_de_pdf(pdf_path)
    chunks = procesar_texto_en_chunks(texto)
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings, dtype=np.float32))
    return index, chunks

# --- Función para responder preguntas ---
def responder_pregunta(pregunta_usuario, k=3):
    pdf_path = obtener_ultimo_pdf()
    if not pdf_path:
        return "No hay ningún PDF disponible para responder preguntas."

    index, text_chunks = construir_indice_desde_pdf(pdf_path)

    query_embedding = embedding_model.encode(pregunta_usuario)
    query_embedding = np.array([query_embedding], dtype=np.float32)
    distances, indices = index.search(query_embedding, k)

    fragmentos = [text_chunks[idx] for idx in indices[0] if idx < len(text_chunks)]
    if not fragmentos:
        return "No se recuperaron fragmentos relevantes."

    contexto = "\n\n".join(fragmentos)
    prompt = f"Pregunta: {pregunta_usuario}\n\nContexto:\n{contexto}\n\nRespuesta:"

    max_prompt_chars = 3500
    if len(prompt) > max_prompt_chars:
        prompt = prompt[:max_prompt_chars]

    respuesta_obj = generator(
        prompt,
        max_new_tokens=80,
        num_return_sequences=1,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id
    )

    respuesta_generada = respuesta_obj[0]['generated_text']
    partes = respuesta_generada.split("Respuesta:")
    return partes[-1].strip() if len(partes) > 1 else respuesta_generada.strip()

# --- Prueba local ---
if __name__ == "__main__":
    pregunta = "¿Qué aprendió el principito del zorro sobre domesticar?"
    print(responder_pregunta(pregunta))
