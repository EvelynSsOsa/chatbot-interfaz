# app.py

import streamlit as st
import os

# Configuración de la página
st.set_page_config(page_title="📘 Pregunta desde PDF", page_icon="🪐", layout="wide")

# Intentar importar la función de respuesta
try:
    from rag_system import responder_pregunta
except ImportError as e:
    st.error(f"❌ No se puede importar responder_pregunta: {e}")
    st.stop()

# Título y subtítulo centrados
st.markdown("<h1 style='text-align: center;'>🪐 Pregúntale a Plugo</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Sube un PDF o elige uno, y pregúntale lo que quieras con ayuda de <b>Plugo</b>.</p>", unsafe_allow_html=True)

# Carpeta donde se guardan los PDFs
CARPETA_PDFS = "pdfs_subidos"
os.makedirs(CARPETA_PDFS, exist_ok=True)

# Subida de archivo PDF
with st.expander("📤 Subir nuevo PDF"):
    archivo = st.file_uploader("Selecciona un archivo PDF:", type="pdf", key="uploader")
    if archivo:
        ruta = os.path.join(CARPETA_PDFS, archivo.name)
        with open(ruta, "wb") as f:
            f.write(archivo.getbuffer())
        st.success(f"✅ PDF '{archivo.name}' subido correctamente.")
        st.rerun()

# Mostrar PDFs disponibles
pdfs = [f for f in os.listdir(CARPETA_PDFS) if f.lower().endswith(".pdf")]
if not pdfs:
    st.warning("Aún no tienes PDFs subidos. Sube uno primero.")
    st.stop()

seleccion = st.selectbox("Selecciona un PDF:", pdfs)

# Input de la pregunta
pregunta = st.text_input("¿Qué quieres saber del PDF?")

# Mostrar respuesta si hay pregunta
if pregunta:
    with st.spinner("Consultando el PDF..."):
        respuesta = responder_pregunta(pregunta, nombre_pdf=seleccion)

    with st.chat_message("assistant"):
        st.markdown(f"🧠 **Plugo dice:**\n\n{respuesta}")
