import streamlit as st
import os

st.set_page_config(page_title="📘 Pregunta desde PDF", page_icon="🪐", layout="wide")

try:
    from rag_system import responder_pregunta
except ImportError as e:
    st.error(f"❌ No se puede importar responder_pregunta: {e}")
    st.stop()

st.title("🪐 Pregúntale a Plugo")
st.markdown("Sube un archivo PDF o selecciona uno ya subido, y hazle preguntas al contenido con ayuda de **Plugo**.")

CARPETA_PDFS = "pdfs_subidos"
os.makedirs(CARPETA_PDFS, exist_ok=True)

# Subida de PDF
with st.expander("📤 Subir nuevo PDF"):
    archivo = st.file_uploader("Selecciona un archivo PDF:", type="pdf")
    if archivo:
        ruta = os.path.join(CARPETA_PDFS, archivo.name)
        with open(ruta, "wb") as f:
            f.write(archivo.getbuffer())
        st.success(f"✅ PDF '{archivo.name}' subido correctamente.")
        st.stop()  # 🔁 Detenemos ejecución para forzar que se recargue al subir

# Verificar PDFs
pdfs = [f for f in os.listdir(CARPETA_PDFS) if f.lower().endswith(".pdf")]
if not pdfs:
    st.warning("⚠️ Aún no tienes PDFs subidos. Sube uno primero.")
    st.stop()

# Elegir PDF
seleccion = st.selectbox("Selecciona un PDF:", pdfs)

# Pregunta
pregunta = st.text_input("¿Qué quieres saber del PDF?")

if pregunta:
    with st.spinner("Consultando el PDF..."):
        try:
            respuesta = responder_pregunta(pregunta, nombre_pdf=seleccion)
            with st.chat_message("assistant"):
                st.markdown(f"🧠 **Plugo dice:**\n\n{respuesta}")
        except Exception as e:
            st.error(f"❌ Ocurrió un error al responder: {e}")
