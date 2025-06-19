import streamlit as st
import os

st.title("📤 Subir nuevo PDF")

CARPETA_DESTINO = "pdfs_subidos"
os.makedirs(CARPETA_DESTINO, exist_ok=True)

archivo_pdf = st.file_uploader("Selecciona un archivo PDF para subirlo", type=["pdf"])
if archivo_pdf:
    ruta_destino = os.path.join(CARPETA_DESTINO, archivo_pdf.name)
    with open(ruta_destino, "wb") as f:
        f.write(archivo_pdf.getbuffer())
    st.success(f"✅ El archivo **{archivo_pdf.name}** se subió correctamente.")
