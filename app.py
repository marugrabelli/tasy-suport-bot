import streamlit as st
import google.generativeai as genai
import os

# Configuración de página
st.set_page_config(page_title="Soporte Tasy Philips", layout="centered")

# Validación de Key con manejo de error explícito
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Error: GOOGLE_API_KEY no encontrada en Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Inicialización de estado
if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None

# --- SELECTOR DE PERFIL ---
if st.session_state.perfil is None:
    st.title("🤖 Soporte Tasy Philips")
    st.subheader("Indica tu perfil profesional para continuar:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Enfermero/a"): st.session_state.perfil = "Enfermería"
    with col2:
        if st.button("Médico/a"): st.session_state.perfil = "Médico"
    with col3:
        if st.button("Otro"): st.session_state.perfil = "General"
    if st.session_state.perfil:
        st.rerun()
    st.stop()

# --- CONFIGURACIÓN ROBUSTA DEL MODELO ---
@st.cache_resource
def load_model(perfil):
    # Intentamos diferentes alias del modelo para evitar el Error 404
    model_names = ["models/gemini-1.5-flash", "gemini-1.5-flash", "models/gemini-pro"]
    instruction = f"Eres un experto en Tasy Philips. Usuario: {perfil}. Usa un tono técnico profesional."
    
    for name in model_names:
        try:
            m = genai.GenerativeModel(model_name=name, system_instruction=instruction)
            # Prueba rápida para verificar si el modelo existe
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except Exception:
            continue
    return None

model = load_model(st.session_state.perfil)

if model is None:
    st.error("No se pudo cargar ningún modelo de Gemini. Revisa tu cuota en Google AI Studio.")
    st.stop()

# --- CHAT UI ---
st.title(f"🤖 Soporte Tasy - {st.session_state.perfil}")

if st.sidebar.button("Nueva Consulta"):
    st.session_state.messages = []
    st.session_state.perfil = None
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe tu consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Forzamos una respuesta limpia sin historial complejo para evitar errores de contexto
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error en la API: {str(e)}")
