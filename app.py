import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime
import os
from docx import Document

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Soporte Tasy Philips", layout="wide")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Configura GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- PERSISTENCIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None
LOG_FILE = "registro_consultas.xlsx"

# --- FUNCIONES TÉCNICAS ---
def leer_docx(ruta):
    try:
        doc = Document(ruta)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error al leer archivo: {e}"

def cargar_contexto(perfil):
    folder = "manuales"
    # Mapeo exacto según tus archivos subidos
    archivos = {
        "Enfermería": "manual enfermeria (2).docx",
        "Médico": "Manual_Medicos.docx",
        "Otro": "Manual Otros profesionales.docx"
    }
    
    file_path = os.path.join(folder, archivos.get(perfil, ""))
    if os.path.exists(file_path):
        return leer_docx(file_path)
    return "No se encontró el manual específico para este perfil."

def guardar_log(perfil, pregunta, respuesta):
    nuevo = pd.DataFrame([{
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Perfil": perfil,
        "Pregunta": pregunta,
        "Respuesta": respuesta
    }])
    if not os.path.isfile(LOG_FILE):
        nuevo.to_excel(LOG_FILE, index=False)
    else:
        try:
            actual = pd.read_excel(LOG_FILE)
            pd.concat([actual, nuevo], ignore_index=True).to_excel(LOG_FILE, index=False)
        except:
            nuevo.to_excel(LOG_FILE, index=False)

# --- PANEL ADMINISTRADOR (Barra Lateral) ---
st.sidebar.title("⚙️ Administración")
if st.sidebar.checkbox("Acceso Admin"):
    clave = st.sidebar.text_input("Password", type="password")
    if clave == "tasy2024":
        st.sidebar.success("Sesión Admin Activa")
        if os.path.exists(LOG_FILE):
            df = pd.read_excel(LOG_FILE)
            st.sidebar.write("### Registro de Consultas")
            st.sidebar.dataframe(df)
            with open(LOG_FILE, "rb") as f:
                st.sidebar.download_button("Descargar Excel", f, file_name=LOG_FILE)
    elif clave:
        st.sidebar.error("Clave incorrecta")

if st.sidebar.button("🔄 Reiniciar App"):
    st.session_state.messages = []
    st.session_state.perfil = None
    st.rerun()

# --- INTERFAZ DE USUARIO ---
if st.session_state.perfil is None:
    st.title("🤖 Soporte Funcional Tasy Philips")
    st.subheader("Para comenzar, selecciona tu perfil profesional:")
    c1, c2, c3 = st.columns(3)
    if c1.button("Enfermero/a"): st.session_state.perfil = "Enfermería"
    if c2.button("Médico/a"): st.session_state.perfil = "Médico"
    if c3.button("Otro Profesional"): st.session_state.perfil = "Otro"
    if st.session_state.perfil: st.rerun()
    st.stop()

# --- LÓGICA DE CHAT ---
st.title(f"Soporte Tasy - Perfil: {st.session_state.perfil}")

# Cargamos el manual correspondiente al perfil seleccionado
with st.spinner("Procesando manual institucional..."):
    contexto_actual = cargar_contexto(st.session_state.perfil)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Escribe tu duda aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt_instruccion = f"""
            Eres un experto analista funcional del sistema Tasy Philips.
            Tu conocimiento base es el siguiente MANUAL INSTITUCIONAL:
            {contexto_actual[:15000]}
            
            Instrucciones:
            1. Responde a un {st.session_state.perfil}.
            2. Usa SOLO la información del manual proporcionado.
            3. Si la respuesta no está en el manual, indícalo cortésmente.
            
            Pregunta del usuario: {prompt}
            """
            
            response = model.generate_content(prompt_instruccion)
            respuesta = response.text
            st.markdown(respuesta)
            
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            guardar_log(st.session_state.perfil, prompt, respuesta)
            
        except Exception as e:
            st.error(f"Error: {e}")
