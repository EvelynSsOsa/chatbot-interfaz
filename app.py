import streamlit as st
import os
from rag_system import responder_pregunta

st.set_page_config(page_title="📘 Preguntar PDF", layout="wide")
st.title("🪐 Pregúntale al PDF")

archivos = [f for f in os.listdir("pdfs_subidos") if f.endswith(".pdf")]
if not archivos:
    st.warning("No hay PDFs subidos todavía. Ve a la pestaña ➕ **Subir PDF**.")
    st.stop()

nombre_pdf = st.selectbox("Elige un PDF:", archivos)
pregunta = st.text_input("Escribe tu pregunta:")

if pregunta:
    with st.spinner("Consultando..."):
        respuesta = responder_pregunta(pregunta, nombre_pdf=nombre_pdf)
    st.success("📗 Respuesta:")
    st.write(respuesta)
