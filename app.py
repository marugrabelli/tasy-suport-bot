import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
from datetime import datetime
from PyPDF2 import PdfReader

# --- CONFIGURACIÓN DE AMBIENTE ---
st.set_page_config(page_title="Soporte Tasy Philips", layout="wide")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- GESTIÓN DE ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None

# --- FUNCIONES DE LECTURA ---
def leer_pdf(nombre_archivo):
    ruta = os.path.join("manuales", nombre_archivo)
    if not os.path.exists(ruta):
        return f"Error: No se encuentra el archivo {nombre_archivo} en la carpeta /manuales."
    try:
        reader = PdfReader(ruta)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        return texto_completo
    except Exception as e:
        return f"Error al procesar el PDF: {e}"

def guardar_log(perfil, pregunta, respuesta):
    log_file = "consultas_tasy.csv"
    nuevo_log = pd.DataFrame([{
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Perfil": perfil,
        "Pregunta": pregunta,
        "Respuesta": respuesta
    }])
    nuevo_log.to_csv(log_file, mode='a', index=False, header=not os.path.exists(log_file))

# --- SIDEBAR: ADMIN Y RESET ---
with st.sidebar:
    st.title("⚙️ Administración")
    if st.checkbox("Acceso Administrador"):
        clave = st.text_input("Contraseña", type="password")
        if clave == "tasy2024":
            if os.path.exists("consultas_tasy.csv"):
                st.write("### Historial de Consultas")
                st.dataframe(pd.read_csv("consultas_tasy.csv"))
    
    if st.button("🔄 Reiniciar Sesión"):
        st.session_state.perfil = None
        st.session_state.messages = []
        st.rerun()

# --- SELECCIÓN DE PERFIL ---
if st.session_state.perfil is None:
    st.title("🤖 Soporte Tasy Philips (PDF Mode)")
    st.subheader("Selecciona tu perfil profesional para comenzar:")
    c1, c2, c3 = st.columns(3)
    if c1.button("Enfermero/a"): st.session_state.perfil = "Enfermería"
    if c2.button("Médico/a"): st.session_state.perfil = "Médico"
    if c3.button("Otro Profesional"): st.session_state.perfil = "Otro"
    if st.session_state.perfil: st.rerun()
    st.stop()

# --- CARGA DE CONTEXTO ---
archivos_pdf = {
    "Enfermería": "enfermeria.pdf",
    "Médico": "medico.pdf",
    "Otro": "otro.pdf"
}
contexto_manual = leer_pdf(archivos_pdf.get(st.session_state.perfil))

# --- CHAT INTERACTIVO ---
st.title(f"Soporte Tasy - {st.session_state.perfil}")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("¿Cuál es tu consulta sobre el sistema?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Instrucción de sistema inyectada en el prompt
            full_prompt = f"""
            Actúa como soporte técnico de Tasy Philips. 
            CONTEXTO DEL MANUAL: {contexto_manual[:15000]}
            
            PREGUNTA DEL USUARIO ({st.session_state.perfil}): {prompt}
            
            Responde basándote solo en el manual. Si no está, sugiere contactar a Sistemas.
            """
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            guardar_log(st.session_state.perfil, prompt, response.text)
        except Exception as e:
            st.error(f"Error en la IA: {e}")
