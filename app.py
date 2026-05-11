import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="Asistente Pro Gemini", layout="centered")
st.title("🤖 Hola! resuelvo tus dudas")

# 2. Validación de Seguridad de la API Key
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la configuración de GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Inicializar el historial del chat (Memoria)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Configuración del Modelo
model = genai.GenerativeModel('gemini-1.5-flash')

# 5. Mostrar mensajes previos del historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Entrada del usuario
if prompt := st.chat_input("¿En qué puedo ayudarte hoy?"):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 7. Generar respuesta de Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # Enviar el historial completo para que tenga contexto (Memoria)
            response = model.generate_content(prompt)
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # Guardar respuesta en el historial
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Hubo un error con la API: {e}")
