import streamlit as st
import google.generativeai as genai
import docx2txt
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Soporte Tasy IA - V2", page_icon="🤖", layout="wide")

# --- 2. CONFIGURACIÓN DE GEMINI API ---
# Recuerda configurar 'GEMINI_API_KEY' en los Secrets de Streamlit Cloud
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ Error: No se encontró la clave GEMINI_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. LÓGICA DE EXTRACCIÓN DE CONOCIMIENTO (RAG) ---
@st.cache_data(show_spinner="Leyendo manuales de soporte...")
def cargar_contexto_manuales():
    texto_acumulado = ""
    # Lista de tus archivos actuales en el repo
    archivos_manuales = [
        "Manual_Medicos.docx", 
        "manual enfermeria (2).docx", 
        "Manual Otros profesionales.docx"
    ]
    
    for archivo in archivos_manuales:
        if os.path.exists(archivo):
            try:
                contenido = docx2txt.process(archivo)
                texto_acumulado += f"\n--- CONTENIDO DEL ARCHIVO {archivo} ---\n{contenido}"
            except Exception as e:
                st.warning(f"No se pudo leer {archivo}: {e}")
    
    return texto_acumulado

# Cargamos el conocimiento una sola vez para ahorrar recursos
contexto_soporte = cargar_contexto_manuales()

# --- 4. INTERFAZ DE USUARIO ---
st.title("🏥 Asistente Funcional Tasy (Versión IA)")
st.info("Esta versión utiliza Inteligencia Artificial para analizar los manuales y responder tus dudas.")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. FLUJO DE CONVERSACIÓN ---
if prompt := st.chat_input("¿En qué puedo ayudarte con el sistema Tasy?"):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta de la IA
    with st.chat_message("assistant"):
        with st.spinner("Consultando manuales..."):
            # Definimos la personalidad del Analista Funcional
            system_instruction = f"""
            Eres un Analista Funcional experto en el sistema Tasy (Philips).
            Tu misión es ayudar al personal de salud (médicos y enfermeros).
            Usa ÚNICAMENTE la información de los manuales que se te proporcionan a continuación.
            Si la información no está en los manuales, responde amablemente que no posees esa información y sugiere contactar a la Mesa de Ayuda.
            
            MANUALES DE REFERENCIA:
            {contexto_soporte}
            """
            
            try:
                # Llamada a Gemini
                response = model.generate_content([system_instruction, prompt])
                respuesta_final = response.text
                
                st.markdown(respuesta_final)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_final})
                
            except Exception as e:
                st.error(f"Hubo un error con la IA: {e}")

# --- 6. BARRA LATERAL (OPCIONAL) ---
with st.sidebar:
    st.header("Estado del Sistema")
    if contexto_soporte:
        st.success("✅ Manuales cargados correctamente")
    else:
        st.error("⚠️ No se encontraron archivos .docx")
    
    st.divider()
    st.write("Versión: 2.0 (RAG + Gemini)")
    st.write("Analista: Marina Grabelli")
