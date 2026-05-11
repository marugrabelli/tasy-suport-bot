import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="Soporte Tasy Philips", layout="centered")

# 2. Validación de API Key
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Estado de la sesión (Memoria y Perfil)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "perfil" not in st.session_state:
    st.session_state.perfil = None

# --- SELECCIÓN DE PERFIL INICIAL ---
if st.session_state.perfil is None:
    st.title("🤖 Soporte Tasy Philips")
    st.subheader("Para comenzar, indica tu perfil profesional:")
    
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

# --- CHAT PRINCIPAL ---
st.title(f"🤖 Soporte Tasy - {st.session_state.perfil}")

if st.sidebar.button("Cambiar Perfil / Nueva Consulta"):
    st.session_state.messages = []
    st.session_state.perfil = None
    st.rerun()

# 4. Configuración del Modelo
# Usamos 'gemini-1.5-flash' directamente
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=f"Eres un experto en Tasy Philips. Tu usuario es {st.session_state.perfil}. Responde dudas técnicas basadas en flujos de manuales."
)

# 5. Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Lógica de Respuesta
if prompt := st.chat_input("Escribe tu consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Iniciamos chat con memoria
            chat = model.start_chat(history=[])
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            if "404" in str(e):
                st.error("Error 404: El servidor aún no reconoce el modelo. Por favor, asegúrate de haber actualizado el archivo requirements.txt en GitHub y reinicia la app.")
            else:
                st.error(f"Error: {e}")
