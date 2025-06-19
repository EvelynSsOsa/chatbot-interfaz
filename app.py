import streamlit as st
import os

st.set_page_config(page_title="📘 Pregunta desde PDF", page_icon="🪐", layout="wide")

try:
    from rag_system import responder_pregunta
except ImportError as e:
    st.error(f"❌ No se puede importar responder_pregunta: {e}")
    st.stop()

st.title(" 🤖 Pregúntale a Plugo")

st.markdown("Sube un archivo PDF o selecciona uno ya subido, y hazle preguntas al contenido con ayuda de Plugo")

# Carpeta
CARPETA_PDFS = "pdfs_subidos"
os.makedirs(CARPETA_PDFS, exist_ok=True)

# 🚀 Subida de PDF en la misma página
with st.expander("📤 Subir nuevo PDF"):
    archivo = st.file_uploader("Selecciona un archivo PDF:", type="pdf", key="uploader")
    if archivo:
        ruta = os.path.join(CARPETA_PDFS, archivo.name)
        with open(ruta, "wb") as f:
            f.write(archivo.getbuffer())
        st.success(f"✅ PDF '{archivo.name}' subido correctamente.")
        st.experimental_rerun()

# Listado de PDFs
pdfs = [f for f in os.listdir(CARPETA_PDFS) if f.lower().endswith(".pdf")]
if not pdfs:
    st.warning("Aún no tienes PDFs subidos. Sube uno primero.")
    st.stop()

seleccion = st.selectbox("Selecciona un PDF:", pdfs)

# Input de pregunta
pregunta = st.text_input("¿Qué quieres saber del PDF?")

if pregunta:
    with st.spinner("Consultando el PDF..."):
        respuesta = responder_pregunta(pregunta, nombre_pdf=seleccion)
    st.success("✅ Respuesta obtenida:")
    st.write(respuesta)
