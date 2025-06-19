import streamlit as st
import os

# --- Intentar importar la función principal ---
try:
    from rag_system import responder_pregunta
    st.success("✅ Importación de rag_system exitosa.")
except Exception as e:
    st.error(f"❌ Error al importar rag_system: {e}")
    st.stop()

# --- Configuración general ---
st.set_page_config(page_title="Pregúntale al Principito", page_icon="🪐")
st.title("🪐 Pregúntale al Principito")

st.markdown("""
¿Tienes una duda sobre el contenido de un PDF que subiste?
Selecciona el archivo y haz tu pregunta.
""")

# --- Carpeta de PDFs ---
carpeta_pdfs = "pdfs_subidos"
os.makedirs(carpeta_pdfs, exist_ok=True)

# --- Bloque para subir nuevos PDFs ---
with st.expander("📤 Subir nuevo PDF"):
    uploaded_pdf = st.file_uploader("Elige un PDF", type=["pdf"])
    if uploaded_pdf is not None:
        ruta_guardado = os.path.join(carpeta_pdfs, uploaded_pdf.name)
        with open(ruta_guardado, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        st.success(f"✅ PDF '{uploaded_pdf.name}' subido con éxito.")
        st.rerun()

# --- Buscar archivos PDF disponibles ---
archivos_pdf = [f for f in os.listdir(carpeta_pdfs) if f.endswith(".pdf")]

if not archivos_pdf:
    st.warning("Aún no has subido ningún PDF. Ve a la pestaña de arriba.")
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
