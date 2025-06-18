# pages/1_Subir_PDF.py

import streamlit as st
import os

# Configurar título de la pestaña
st.title("📤 Subir nuevo PDF")

# Crear carpeta si no existe
CARPETA_DESTINO = "pdfs_subidos"
os.makedirs(CARPETA_DESTINO, exist_ok=True)

# Subir archivo PDF
archivo_pdf = st.file_uploader("Selecciona un archivo PDF para subirlo", type=["pdf"])

if archivo_pdf is not None:
    # Guardar archivo
    ruta_destino = os.path.join(CARPETA_DESTINO, archivo_pdf.name)
    
    with open(ruta_destino, "wb") as f:
        f.write(archivo_pdf.getbuffer())

    st.success(f"✅ El archivo **{archivo_pdf.name}** ha sido subido con éxito a la carpeta `{CARPETA_DESTINO}/`.")
