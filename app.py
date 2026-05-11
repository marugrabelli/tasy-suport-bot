import streamlit as st
import google.generativeai as genai

# 1. Configuración básica
st.set_page_config(page_title="Soporte Tasy", layout="centered")

# 2. Conexión con la Key (Usa el nombre exacto de tus Secrets)
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la GOOGLE_API_KEY en Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. Estado de la sesión
if "perfil" not in st.session_state:
    st.session_state.perfil = None
if "chat" not in st.session_state:
    st.session_state.chat = []

# --- PANTALLA DE INICIO: SELECCIÓN DE PERFIL ---
if st.session_state.perfil is None:
    st.title("🤖 Soporte Tasy Philips")
    st.write("Seleccioná tu perfil para continuar:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Enfermería"):
            st.session_state.perfil = "Enfermería"
            st.rerun()
    with col2:
        if st.button("Médico"):
            st.session_state.perfil = "Médico"
            st.rerun()
    st.stop()

# --- INTERFAZ DE CHAT ---
st.title(f"Soporte Tasy - {st.session_state.perfil}")

# Botón para resetear
if st.sidebar.button("Cambiar Perfil"):
    st.session_state.perfil = None
    st.session_state.chat = []
    st.rerun()

# Configurar el modelo (usamos gemini-pro como alternativa si el flash falla)
model_name = 'gemini-1.5-flash'
model = genai.GenerativeModel(model_name)

# Mostrar mensajes
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Entrada de usuario
if prompt := st.chat_input("¿Cuál es tu duda?"):
    # Guardar mensaje del usuario
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generar respuesta
    with st.chat_message("assistant"):
        try:
            # Instrucción de contexto directa en la consulta
            contexto = f"Actúa como soporte técnico de Tasy Philips para el área de {st.session_state.perfil}. Pregunta: {prompt}"
            response = model.generate_content(contexto)
            
            respuesta_texto = response.text
            st.write(respuesta_texto)
            st.session_state.chat.append({"role": "assistant", "content": respuesta_texto})
            
        except Exception as e:
            # Si falla el 1.5, intentamos con el Pro automáticamente
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                response = model_alt.generate_content(contexto)
                st.write(response.text)
                st.session_state.chat.append({"role": "assistant", "content": response.text})
            except Exception as e_final:
                st.error(f"Error crítico: {e_final}")
