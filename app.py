import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="Asistente de Soporte Tasy", layout="wide")

# 2. Validación de Seguridad de la API Key en Secrets
# Asegúrate de que en Streamlit Secrets diga exactamente: GOOGLE_API_KEY = "tu_clave"
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
    st.stop() 

# --- INTERFAZ PRINCIPAL DEL CHAT ---
st.title(f"🤖 Soporte Tasy - Perfil: {st.session_state.perfil}")
st.caption(f"Consultando manuales específicos para el área de {st.session_state.perfil.lower()}.")

# Botón para reiniciar en la barra lateral
if st.sidebar.button("Reiniciar Sesión / Cambiar Perfil"):
    st.session_state.messages = []
    st.session_state.perfil = None
    st.rerun()

# 4. Configuración del Modelo
# Nota: Si el error 404 persiste, intentamos con el nombre completo del modelo
try:
    instruction = f"Eres un experto en el sistema Tasy Philips. Tu usuario tiene perfil de {st.session_state.perfil}. Responde de forma técnica y clara basándote en manuales institucionales."
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=instruction
    )
except Exception:
    # Fallback por si la versión de la librería es muy vieja
    model = genai.GenerativeModel('gemini-pro')

# 5. Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Entrada del usuario y lógica de respuesta
if prompt := st.chat_input("Escribe tu duda sobre el sistema aquí..."):
    # Guardar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # Usamos start_chat para mantener la memoria de la conversación
            chat = model.start_chat(history=[])
            # Enviamos el contexto del perfil junto con la consulta
            response = chat.send_message(f"Perfil de usuario: {st.session_state.perfil}. Consulta: {prompt}")
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # Guardar respuesta en el historial
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error de conexión: {str(e)}")
            st.info("Prueba actualizar la librería google-generativeai en tu requirements.txt")
