import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime
import os
from docx import Document

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Soporte Tasy Philips", layout="wide")

# Validación de Key con el nombre exacto de tus Secrets
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Error: No se encontró la GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 2. GESTIÓN DE ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None
LOG_FILE = "consultas_tasy.xlsx"

# --- 3. FUNCIONES TÉCNICAS ---
def leer_docx(ruta):
    try:
        doc = Document(ruta)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error al leer el archivo: {e}"

def cargar_manual_por_perfil(perfil):
    ruta_base = "manuales"
    # Mapeo exacto según tus nombres de archivos en la carpeta de GitHub
    archivos = {
        "Enfermería": "manual enfermeria (2).docx",
        "Médico": "Manual_Medicos.docx",
        "Otro Profesional": "Manual Otros profesionales.docx"
    }
    
    archivo_nombre = archivos.get(perfil)
    if archivo_nombre:
        ruta_completa = os.path.join(ruta_base, archivo_nombre)
        if os.path.exists(ruta_completa):
            return leer_docx(ruta_completa)
    return "No se encontró el manual correspondiente en la carpeta /manuales."

def guardar_consulta_excel(perfil, pregunta, respuesta):
    nuevo_dato = pd.DataFrame([{
        "Fecha/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Perfil": perfil,
        "Pregunta": pregunta,
        "Respuesta": respuesta
    }])
    
    if not os.path.exists(LOG_FILE):
        nuevo_dato.to_excel(LOG_FILE, index=False)
    else:
        try:
            actual = pd.read_excel(LOG_FILE)
            pd.concat([actual, nuevo_dato], ignore_index=True).to_excel(LOG_FILE, index=False)
        except:
            nuevo_dato.to_excel(LOG_FILE, index=False)

# --- 4. BARRA LATERAL (ADMIN Y RESET) ---
st.sidebar.title("🛠️ Panel de Control")

if st.sidebar.checkbox("Modo Administrador"):
    clave = st.sidebar.text_input("Contraseña de acceso", type="password")
    if clave == "tasy2024":
        st.sidebar.success("Acceso Admin concedido")
        if os.path.exists(LOG_FILE):
            df_logs = pd.read_excel(LOG_FILE)
            st.sidebar.write("### Registro Histórico de Consultas")
            st.sidebar.dataframe(df_logs)
            with open(LOG_FILE, "rb") as f:
                st.sidebar.download_button("Descargar Reporte (Excel)", f, file_name=LOG_FILE)
    elif clave:
        st.sidebar.error("Contraseña incorrecta")

if st.sidebar.button("🔄 Cambiar Perfil / Nueva Sesión"):
    st.session_state.messages = []
    st.session_state.perfil = None
    st.rerun()

# --- 5. FLUJO DE USUARIO ---
if st.session_state.perfil is None:
    st.title("🤖 Soporte Funcional Tasy Philips")
    st.subheader("Bienvenido/a. Para comenzar, indica tu perfil:")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Enfermero/a"): st.session_state.perfil = "Enfermería"
    if c2.button("Médico/a"): st.session_state.perfil = "Médico"
    if c3.button("Otro Profesional"): st.session_state.perfil = "Otro Profesional"
    
    if st.session_state.perfil:
        st.rerun()
    st.stop()

# --- 6. CHAT INTERACTIVO ---
st.title(f"Soporte Tasy - {st.session_state.perfil}")

# Carga de contexto del manual según perfil seleccionado
with st.spinner("Sincronizando con manuales institucionales..."):
    contexto_manual = cargar_manual_por_perfil(st.session_state.perfil)

# Mostrar historial de chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada de pregunta
if prompt := st.chat_input("¿En qué puedo ayudarte con el sistema Tasy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Construcción del prompt incluyendo el contenido del Word
            prompt_con_contexto = f"""
            Eres un asistente técnico experto en el sistema Tasy Philips.
            Tu conocimiento base es el siguiente MANUAL DE PROCEDIMIENTOS:
            ---
            {contexto_manual[:15000]}
            ---
            Instrucciones de respuesta:
            1. Responde a un usuario con perfil profesional de: {st.session_state.perfil}.
            2. Usa EXCLUSIVAMENTE la información contenida en el manual de arriba.
            3. Si la respuesta no figura en el manual, responde exactamente: 'Lo siento, esa información no figura en el manual institucional actual. Por favor, consulta con el referente de Sistemas de tu sector.'
            
            Pregunta del usuario: {prompt}
            """
            
            response = model.generate_content(prompt_con_contexto)
            respuesta_texto = response.text
            
            st.markdown(respuesta_texto)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
            
            # Registro automático en el archivo Excel
            guardar_consulta_excel(st.session_state.perfil, prompt, respuesta_texto)
            
        except Exception as e:
            st.error(f"Hubo un problema al procesar la respuesta: {e}")
