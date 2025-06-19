import streamlit as st
import os

# --- Intentar importar la función principal del sistema RAG ---
try:
    from rag_system import responder_pregunta
except Exception as e:
    st.error(f"❌ Error al importar rag_system: {e}")
    st.stop()

# --- Configuración de la página ---
st.set_page_config(page_title="Pregúntale al Principito", page_icon="🪐")
st.title("🪐 Pregúntale al Principito")

st.markdown("""
¿Tienes una duda sobre el contenido de un PDF que subiste?
Selecciona el archivo y haz tu pregunta.
""")

# --- Verificar si hay archivos PDF disponibles ---
carpeta_pdfs = "pdfs_subidos"
if not os.path.exists(carpeta_pdfs):
    os.makedirs(carpeta_pdfs)

archivos_pdf = [f for f in os.listdir(carpeta_pdfs) if f.endswith(".pdf")]

if not archivos_pdf:
    st.warning("Aún no has subido ningún PDF. Ve a la pestaña 'Subir PDF'.")
    st.stop()

# --- Menú desplegable para elegir PDF ---
nombre_pdf = st.selectbox("Selecciona un archivo PDF:", archivos_pdf)

# --- Input de la pregunta ---
pregunta = st.text_input("Escribe tu pregunta aquí:")

# --- Llamar a responder_pregunta si hay input ---
if pregunta:
    with st.spinner("Consultando..."):
        respuesta = responder_pregunta(pregunta, nombre_pdf=nombre_pdf)
    st.success("Respuesta:")
    st.write(respuesta)

