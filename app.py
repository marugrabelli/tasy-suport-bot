import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
st.set_page_config(page_title="Soporte Tasy Philips", layout="centered")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Configura GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 2. GESTIÓN DE ESTADO (MEMORIA) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None
if "log_file" not in st.session_state:
    st.session_state.log_file = "registro_consultas.xlsx"

# --- 3. FUNCIÓN PARA GUARDAR LOGS EN EXCEL ---
def guardar_log(perfil, pregunta, respuesta):
    nuevo_registro = {
        "Fecha/Hora": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Perfil": [perfil],
        "Pregunta": [pregunta],
        "Respuesta": [respuesta]
    }
    df_nuevo = pd.DataFrame(nuevo_registro)
    
    if not os.path.isfile(st.session_state.log_file):
        df_nuevo.to_excel(st.session_state.log_file, index=False)
    else:
        with pd.ExcelWriter(st.session_state.log_file, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
            # Leer el archivo actual para añadir al final
            df_actual = pd.read_excel(st.session_state.log_file)
            df_final = pd.concat([df_actual, df_nuevo], ignore_index=True)
            df_final.to_excel(writer, index=False)

# --- 4. SELECCIÓN DE PERFIL PROFESIONAL ---
if st.session_state.perfil is None:
    st.title("🤖 Soporte Tasy Philips")
    st.subheader("Para comenzar, indica tu perfil:")
    
    # Restablecidos los 3 perfiles originales
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Enfermero/a"): 
            st.session_state.perfil = "Enfermería"
            st.rerun()
    with col2:
        if st.button("Médico/a"): 
            st.session_state.perfil = "Médico"
            st.rerun()
    with col3:
        if st.button("Otro Profesional"): 
            st.session_state.perfil = "Otro"
            st.rerun()
    st.stop()

# --- 5. CONFIGURACIÓN DEL MODELO (Basado en Manuales) ---
# Se le instruye al modelo que su conocimiento base son los manuales cargados en el repositorio
instruccion_base = f"""
Actúa como un experto soporte funcional de Tasy Philips. 
Tu base de conocimiento son los manuales institucionales cargados en este repositorio.
El usuario es un {st.session_state.perfil}. 
Responde de forma técnica, precisa y basada estrictamente en los procesos de los manuales.
Si no estás seguro, pide que se contacte al líder de proyecto Tasy.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instruccion_base
)

# --- 6. INTERFAZ DE CHAT ---
st.title(f"Soporte Tasy - {st.session_state.perfil}")

if st.sidebar.button("Nueva Consulta / Cambiar Perfil"):
    st.session_state.messages = []
    st.session_state.perfil = None
    st.rerun()

# Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada de usuario
if prompt := st.chat_input("¿En qué puedo ayudarte con Tasy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Crear hilo de chat con memoria del hilo actual
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(prompt)
            respuesta_texto = response.text
            
            st.markdown(respuesta_texto)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
            
            # Guardar automáticamente en el Excel
            guardar_log(st.session_state.perfil, prompt, respuesta_texto)
            
        except Exception as e:
            st.error(f"Error en la consulta: {e}")

# Botón opcional para descargar el Excel de logs
if os.path.exists(st.session_state.log_file):
    with open(st.session_state.log_file, "rb") as f:
        st.sidebar.download_button("Descargar Registro de Consultas", f, file_name="consultas_tasy.xlsx")
