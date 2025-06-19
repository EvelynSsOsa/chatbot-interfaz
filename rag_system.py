# rag_system.py
import os
import faiss
import numpy as np
import torch
import pickle
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from pdf_extractor import extraer_texto_de_pdf

# --- Modelos globales ---
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
modelo_llm = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")
generator = pipeline(
    "text-generation",
    model=modelo_llm,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1
)

# --- Obtener el PDF más reciente ---
def obtener_ultimo_pdf():
    carpeta = "pdfs_subidos"
    archivos = [f for f in os.listdir(carpeta) if f.endswith(".pdf")]
    if not archivos:
        return None
    archivos.sort(key=lambda f: os.path.getmtime(os.path.join(carpeta, f)), reverse=True)
    return archivos[0]  # solo el nombre del archivo

# --- Cargar .index y .pkl si existen ---
def cargar_indice_y_chunks(nombre_base_sin_ext):
    index_path = f"{nombre_base_sin_ext}.index"
    pkl_path = f"{nombre_base_sin_ext}_text_chunks.pkl"

    if not os.path.exists(index_path) or not os.path.exists(pkl_path):
        return None, None

    index = faiss.read_index(index_path)
    with open(pkl_path, "rb") as f:
        text_chunks = pickle.load(f)
    return index, text_chunks

# --- Crear nuevo índice FAISS y guardar ---
def construir_y_guardar(nombre_base_sin_ext, pdf_path):
    texto = extraer_texto_de_pdf(pdf_path)
    chunks = procesar_texto_en_chunks(texto)
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings, dtype=np.float32))

    # Guardar .index y .pkl
    faiss.write_index(index, f"{nombre_base_sin_ext}.index")
    with open(f"{nombre_base_sin_ext}_text_chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    return index, chunks

def responder_pregunta(pregunta_usuario, k=3, nombre_pdf=None):
    if nombre_pdf is None:
        nombre_pdf = obtener_ultimo_pdf()
        if not nombre_pdf:
            return "❌ No hay ningún PDF cargado."

    nombre_pdf = nombre_pdf.replace(".pdf", "")
    nombre_base = nombre_pdf  # sin carpeta para que los .index y .pkl estén en raíz
    pdf_path = os.path.join("pdfs_subidos", nombre_pdf + ".pdf")

    index, chunks = cargar_indice_y_chunks(nombre_base)
    if index is None or chunks is None:
        index, chunks = construir_y_guardar(nombre_base, pdf_path)

    query_embedding = embedding_model.encode(pregunta_usuario)
    query_embedding = np.array([query_embedding], dtype=np.float32)
    distances, indices = index.search(query_embedding, k)

    fragmentos = [chunks[idx] for idx in indices[0] if idx < len(chunks)]
    if not fragmentos:
        return "❌ No se recuperaron fragmentos relevantes."

    contexto = "\n\n".join(fragmentos)
    prompt = f"Pregunta: {pregunta_usuario}\n\nContexto:\n{contexto}\n\nRespuesta:"

    if len(prompt) > 3500:
        prompt = prompt[:3500]

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


# --- Prueba local (opcional) ---
if __name__ == "__main__":
    print(responder_pregunta("¿Qué aprendió el principito del zorro sobre domesticar?"))
def procesar_texto_en_chunks(texto: str):
    from sentence_transformers import SentenceTransformer
    import numpy as np

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    paragraphs = [p.strip() for p in texto.split('\n\n') if p.strip()]
    chunks_with_embeddings = []
    for paragraph in paragraphs:
        cleaned_paragraph = paragraph.replace('\n', ' ').replace('  ', ' ')
        embedding = model.encode(cleaned_paragraph)
        chunks_with_embeddings.append({
            'text': paragraph,
            'embedding': embedding
        })
    return chunks_with_embeddings
