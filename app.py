import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime
import os

# Intentamos importar docx con manejo de error para diagnóstico
try:
    from docx import Document
except ImportError:
    st.error("⚠️ La librería 'python-docx' no está instalada. Revisá el requirements.txt.")
    st.stop()

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Soporte Tasy Philips", layout="wide")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ No se encontró GOOGLE_API_KEY en Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None
LOG_FILE = "registro_consultas.xlsx"

# --- FUNCIONES ---
def leer_docx(ruta):
    try:
        doc = Document(ruta)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"Error leyendo archivo: {e}"

def cargar_contexto(perfil):
    archivos = {
        "Enfermería": "manual enfermeria (2).docx",
        "Médico": "Manual_Medicos.docx",
        "Otro": "Manual Otros profesionales.docx"
    }
    ruta = os.path.join("manuales", archivos.get(perfil, ""))
    if os.path.exists(ruta):
        return leer_docx(ruta)
    return "Manual no encontrado."

def guardar_log(perfil, pregunta, respuesta):
    nuevo = pd.DataFrame([{"Fecha": datetime.now(), "Perfil": perfil, "Pregunta": pregunta, "Respuesta": respuesta}])
    if not os.path.exists(LOG_FILE):
        nuevo.to_excel(LOG_FILE, index=False)
    else:
        try:
            actual = pd.read_excel(LOG_FILE)
            pd.concat([actual, nuevo], ignore_index=True).to_excel(LOG_FILE, index=False)
        except: pass

# --- UI SIDEBAR ---
st.sidebar.title("Administración")
if st.sidebar.checkbox("Acceso Admin"):
    if st.sidebar.text_input("Password", type="password") == "tasy2024":
        if os.path.exists(LOG_FILE):
            st.sidebar.dataframe(pd.read_excel(LOG_FILE))
            with open(LOG_FILE, "rb") as f:
                st.sidebar.download_button("Descargar Excel", f, file_name=LOG_FILE)

if st.sidebar.button("Reiniciar"):
    st.session_state.messages = []
    st.session_state.perfil = None
    st.rerun()

# --- FLUJO PRINCIPAL ---
if st.session_state.perfil is None:
    st.title("🤖 Soporte Tasy")
    c1, c2, c3 = st.columns(3)
    if c1.button("Enfermería"): st.session_state.perfil = "Enfermería"
    if c2.button("Médico"): st.session_state.perfil = "Médico"
    if c3.button("Otro"): st.session_state.perfil = "Otro"
    if st.session_state.perfil: st.rerun()
    st.stop()

st.title(f"Soporte Tasy - {st.session_state.perfil}")
contexto = cargar_contexto(st.session_state.perfil)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("¿Tu duda?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(f"Contexto: {contexto[:15000]}\nPregunta: {prompt}")
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            guardar_log(st.session_state.perfil, prompt, res.text)
        except Exception as e:
            st.error(f"Error IA: {e}")
            
        except Exception as e:
            st.error(f"Hubo un problema al procesar la respuesta: {e}")
