# app.py

import streamlit as st
from rag_system import responder_pregunta

st.set_page_config(page_title="🪐 Pregúntale a tu PDF", page_icon="📄")
st.title("📄 Pregúntale a tu PDF")

st.markdown("""
¿Tienes una duda sobre el contenido de un PDF que subiste?
Escribe tu pregunta abajo y el sistema te responderá usando el contenido del documento.
""")

# Entrada de la pregunta
pregunta = st.text_input("Escribe tu pregunta aquí:")

# Evaluar la pregunta
if pregunta:
    with st.spinner("Buscando respuesta..."):
        respuesta = responder_pregunta(pregunta)
    st.success("Respuesta:")
    st.write(respuesta)


