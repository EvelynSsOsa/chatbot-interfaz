import streamlit as st
import os
from rag_system import responder_pregunta

st.set_page_config(page_title="Pregúntale al Principito", page_icon="🪐")
st.title("🪐 Pregúntale al Principito")

st.markdown("""
¿Tienes una duda sobre el contenido de un PDF que subiste?
Selecciona el archivo y haz tu pregunta.
""")

# --- Buscar archivos PDF disponibles ---
carpeta_pdfs = "pdfs_subidos"
archivos_pdf = [f for f in os.listdir(carpeta_pdfs) if f.endswith(".pdf")]

if not archivos_pdf:
    st.warning("Aún no has subido ningún PDF. Ve a la pestaña 'Subir PDF'.")
    st.stop()

# --- Menú desplegable para elegir PDF ---
nombre_pdf = st.selectbox("Selecciona un archivo PDF:", archivos_pdf)

# --- Input de la pregunta ---
pregunta = st.text_input("Escribe tu pregunta aquí:")

if pregunta:
    with st.spinner("Consultando..."):
        respuesta = responder_pregunta(pregunta, nombre_pdf=nombre_pdf)
    st.success("Respuesta:")
    st.write(respuesta)
