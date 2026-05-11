import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
from datetime import datetime
from PyPDF2 import PdfReader

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Soporte Tasy Philips", layout="wide")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura GOOGLE_API_KEY en Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None

# --- LECTURA DE PDF ---
def leer_pdf(nombre_archivo):
    ruta = os.path.join("manuales", nombre_archivo)
    texto = ""
    if os.path.exists(ruta):
        try:
            reader = PdfReader(ruta)
            for page in reader.pages:
                texto += page.extract_text() + "\n"
        except Exception as e:
            return f"Error leyendo PDF: {e}"
    return texto

# --- SIDEBAR ---
with st.sidebar:
    if st.checkbox("Administrador"):
        if st.text_input("Clave", type="password") == "tasy2024":
            if os.path.exists("consultas.csv"):
                st.dataframe(pd.read_csv("consultas.csv"))
    if st.button("Reiniciar Sesión"):
        st.session_state.perfil = None
        st.session_state.messages = []
        st.rerun()

# --- INTERFAZ ---
if st.session_state.perfil is None:
    st.title("🤖 Soporte Tasy Philips")
    col1, col2, col3 = st.columns(3)
    if col1.button("Enfermería"): st.session_state.perfil = "Enfermería"
    if col2.button("Médico"): st.session_state.perfil = "Médico"
    if col3.button("Otro Profesional"): st.session_state.perfil = "Otro"
    if st.session_state.perfil: st.rerun()
    st.stop()

# Carga automática del manual según el nombre que mostraste
mapeo = {
    "Enfermería": "enfermeria.pdf",
    "Médico": "medico.pdf",
    "Otro": "otros.pdf"
}

contexto = leer_pdf(mapeo.get(st.session_state.perfil))

st.title(f"Soporte Tasy - {st.session_state.perfil}")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Duda técnica..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            instruccion = f"Contexto del manual: {contexto[:15000]}\nPregunta: {prompt}"
            response = model.generate_content(instruccion)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # Log en CSV (más liviano que Excel)
            log = pd.DataFrame([{"Fecha": datetime.now(), "Perfil": st.session_state.perfil, "Pregunta": prompt, "Respuesta": response.text}])
            log.to_csv("consultas.csv", mode='a', index=False, header=not os.path.exists("consultas.csv"))
        except Exception as e:
            st.error(f"Error: {e}")
