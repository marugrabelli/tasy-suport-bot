import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="Asistente de Soporte Tasy", layout="wide")

# 2. Validación de Seguridad de la API Key en Secrets
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Error: No se encontró la clave GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Inicialización de variables de estado (Memoria y Perfil)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None

# --- LÓGICA DE BIENVENIDA Y SELECCIÓN DE PERFIL ---
if st.session_state.perfil is None:
    st.title("🤖 Asistente de Soporte Institucional")
    st.subheader("Bienvenido/a. Para asistirte mejor, por favor indica tu perfil:")
    
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
        if st.button("Otro"):
            st.session_state.perfil = "General"
            st.rerun()
    st.stop() # Detiene la ejecución hasta que elijan un perfil

# --- INTERFAZ PRINCIPAL DEL CHAT ---
st.title(f"🤖 Soporte Tasy - Perfil: {st.session_state.perfil}")
st.caption(f"Consultando manuales específicos para el área de {st.session_state.perfil.lower()}.")

# Botón para limpiar chat
if st.sidebar.button("Limpiar conversación"):
    st.session_state.messages = []
    st.session_state.perfil = None
    st.rerun()

# 4. Instrucción de Sistema (Contexto para Gemini)
# Aquí defines cómo debe comportarse según el manual
system_instruction = f"""
Actúa como un experto en el sistema Tasy Philips. Tu usuario tiene el perfil de {st.session_state.perfil}.
Debes responder de forma técnica, clara y empática, basándote en los flujos de trabajo de los manuales institucionales.
Si la duda es de {st.session_state.perfil}, prioriza los pasos específicos para esa área.
Si no conoces la respuesta exacta, sugiere contactar al equipo de sistemas local.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=system_instruction
)

# 5. Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Entrada del usuario y lógica de respuesta
if prompt := st.chat_input("Escribe tu duda sobre el sistema aquí..."):
    # Guardar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user
