import streamlit as st
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# Configuración
st.set_page_config(page_title="Procesar PDF", page_icon="🧠")
st.title("🧠 Procesar PDF y Generar Índice FAISS")

# Ruta de PDFs
pdf_dir = "pdfs_subidos/"

# Mostrar archivos PDF disponibles
archivos_pdf = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

if not archivos_pdf:
    st.warning("No hay archivos PDF en la carpeta pdfs_subidos/")
else:
    selected_pdf = st.selectbox("Selecciona un PDF para procesar:", archivos_pdf)

    if st.button("Procesar PDF"):
        ruta_pdf = os.path.join(pdf_dir, selected_pdf)

        with st.spinner("Extrayendo texto del PDF..."):
            reader = PdfReader(ruta_pdf)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() + "\n"

        # Dividir en párrafos o fragmentos
        st.info("Dividiendo el texto en fragmentos...")
        fragments = [p.strip().replace("\n", " ") for p in texto.split("\n\n") if len(p.strip()) > 30]

        st.write(f"Se encontraron {len(fragments)} fragmentos.")

        # Generar embeddings
        st.info("Generando embeddings...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        embeddings = [model.encode(frag) for frag in fragments]
        embeddings_np = np.array(embeddings, dtype=np.float32)

        # Crear índice FAISS
        st.info("Creando índice FAISS...")
        dim = embeddings_np.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings_np)

        # Guardar índice y textos
        base_name = os.path.splitext(selected_pdf)[0]
        index_path = f"{base_name}.index"
        pkl_path = f"{base_name}_text_chunks.pkl"

        faiss.write_index(index, index_path)
        with open(pkl_path, "wb") as f:
            pickle.dump(fragments, f)

        st.success(f"✅ Procesamiento completo. Archivos guardados:")
        st.code(f"- {index_path}\n- {pkl_path}", language="text")


