import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
from datetime import datetime
from PyPDF2 import PdfReader

# --- CONFIGURACIÓN DE SEGURIDAD ---
st.set_page_config(page_title="Soporte Tasy Philips", layout="wide")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Error: GOOGLE_API_KEY no configurada en Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- FUNCIONES DE NÚCLEO ---
def extraer_texto_pdf(nombre_archivo):
    # Ruta relativa a la carpeta 'manuales' que creaste
    ruta = os.path.join("manuales", nombre_archivo)
    texto = ""
    if os.path.exists(ruta):
        try:
            reader = PdfReader(ruta)
            for page in reader.pages:
                texto += page.extract_text() + "\n"
            return texto
        except Exception as e:
            return f"Error al leer el PDF {nombre_archivo}: {e}"
    return f"Archivo {nombre_archivo} no encontrado en la carpeta manuales."

def registrar_log(perfil, pregunta, respuesta):
    log_file = "logs_soporte.csv"
    nuevo_log = pd.DataFrame([{
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Perfil": perfil,
        "Pregunta": pregunta,
        "Respuesta": respuesta[:200] # Guardamos un resumen
    }])
    nuevo_log.to_csv(log_file, mode='a', index=False, header=not os.path.exists(log_file))

# --- INTERFAZ Y ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None

# Sidebar con Panel Admin
with st.sidebar:
    st.title("Panel de Control")
    if st.checkbox("Modo Administrador"):
        if st.text_input("Password", type="password") == "tasy2024":
            if os.path.exists("logs_soporte.csv"):
                st.write("### Historial de consultas")
                st.dataframe(pd.read_csv("logs_soporte.csv"))
    
    if st.button("Reiniciar App"):
        st.session_state.perfil = None
        st.session_state.messages = []
        st.rerun()

# --- FLUJO DE USUARIO ---
if st.session_state.perfil is None:
    st.title("🤖 Asistente Tasy Philips")
    st.subheader("Selecciona tu perfil profesional:")
    col1, col2, col3 = st.columns(3)
    if col1.button("Enfermería"): st.session_state.perfil = "Enfermería"
    if col2.button("Médico"): st.session_state.perfil = "Médico"
    if col3.button("Otros Profesionales"): st.session_state.perfil = "Otros"
    if st.session_state.perfil: st.rerun()
    st.stop()

# Carga de contexto (Mapeo exacto según tus archivos)
mapeo_archivos = {
    "Enfermería": "enfermeria.pdf",
    "Médico": "medico.pdf",
    "Otros": "otros.pdf"
}

contexto = extraer_texto_pdf(mapeo_archivos.get(st.session_state.perfil))

st.title(f"Soporte Tasy - Perfil: {st.session_state.perfil}")

# Mostrar Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Escribe tu consulta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Forzamos a la IA a leer el contexto extraído del PDF
            input_ia = f"Soporte Tasy. Manual: {contexto[:15000]}. Pregunta: {prompt}"
            response = model.generate_content(input_ia)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            registrar_log(st.session_state.perfil, prompt, response.text)
        except Exception as e:
            st.error(f"Error en la IA: {e}")
