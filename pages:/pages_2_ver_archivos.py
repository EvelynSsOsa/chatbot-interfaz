# pages/2_Procesar_PDF.py
import streamlit as st
import os
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from text_processor import dividir_texto_en_chunks, extraer_texto_de_pdf

st.set_page_config(page_title="Procesar PDF Subido", page_icon="⚙️")
st.title("⚙️ Procesar PDF Subido")

# Ruta de los PDFs subidos
pdf_dir = "pdfs_subidos"

# Listar PDFs disponibles
pdfs = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

if not pdfs:
    st.warning("No hay archivos PDF disponibles. Sube uno primero en la página 'Subir PDF'.")
    st.stop()

pdf_seleccionado = st.selectbox("Selecciona un PDF para procesar:", pdfs)

if st.button("Procesar este PDF"):
    with st.spinner("Extrayendo texto y generando embeddings..."):
        ruta_pdf = os.path.join(pdf_dir, pdf_seleccionado)
        texto = extraer_texto_de_pdf(ruta_pdf)
        chunks = dividir_texto_en_chunks(texto)

        modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        chunks_with_embeddings = []
        for fragmento in chunks:
            embedding = modelo.encode(fragmento)
            chunks_with_embeddings.append({"text": fragmento, "embedding": embedding})

        # Guardar textos
        textos = [c["text"] for c in chunks_with_embeddings]
        with open("principito_text_chunks.pkl", "wb") as f:
            pickle.dump(textos, f)

        # Guardar índice
        embeddings = np.array([c["embedding"] for c in chunks_with_embeddings], dtype=np.float32)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        faiss.write_index(index, "principito.index")

    st.success("¡PDF procesado correctamente! Ya puedes hacer preguntas desde la página principal.")
