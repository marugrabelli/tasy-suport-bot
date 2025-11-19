import streamlit as st
import csv
import os
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Soporte Tasy FLENI", page_icon="🏥", layout="centered")

# Archivo donde se guardarán las consultas para análisis del equipo
LOG_FILE = "registro_consultas_tasy.csv"

# --- FUNCIONES DE BACKEND ---

def log_interaction(rol, pregunta, respuesta):
    """Guarda la interacción para futuros análisis del equipo."""
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Fecha", "Hora", "Rol", "Pregunta", "Respuesta_Bot"])
        
        now = datetime.now()
        writer.writerow([now.date(), now.strftime("%H:%M:%S"), rol, pregunta, respuesta])

def obtener_contexto_por_rol(rol):
    """Define qué manuales priorizar según el rol seleccionado."""
    if rol == "Enfermería":
        return """
        [PRIORIDAD: MANUAL ENFERMERÍA]
        Temas clave: Signos vitales, ADEP (Medicación), Balance Hídrico, Pendientes de Enfermería.
        Recordatorio: En ADEP, 'Guardar' es borrador, 'Liberar' es publicar.
        Legacy: Para ver historial viejo, consultar SIDCA desde botón derecho (CES).
        """
    elif rol == "Médico / Multi":
        return """
        [PRIORIDAD: MANUAL HOSPITALIZACIÓN MULTI]
        Temas clave: Evoluciones (Notas Clínicas), Informe Final, CPOE, Agenda.
        Recordatorio: El Informe Final requiere estatus 'Realizado' antes de ejecutar el PDF.
        Legacy: SIDCA disponible para consultas históricas.
        """
    return ""

# --- SYSTEM PROMPT (CEREBRO) ---
def generar_system_prompt(rol):
    base_prompt = f"""
    Actúa como un experto en soporte del sistema Tasy para FLENI. Tu usuario actual es un: {rol}.
    
    OBJETIVOS:
    1. **Guiar con Rutas:** Usa formato de flechas para los menús (ej: **Historia Clínica > ADEP > Administrar**).
    2. **Gestión del Cambio:** Si el usuario parece frustrado o confuso, recuerda con empatía que Tasy requiere más pasos de validación que el sistema anterior para garantizar la seguridad del paciente.
    3. **Errores Frecuentes:**
       - Siempre distingue entre GUARDAR (Borrador) y LIBERAR (Finalizar).
       - Recuerda verificar el Sector y Perfil en la esquina superior derecha.
    4. **Tono:** Profesional, paciente y didáctico.
    
    Si te preguntan por algo del sistema anterior, recuérdales que pueden acceder a la "Consulta Electrónica de Salud (CES - SIDCA)" haciendo clic derecho en el fondo blanco de la historia clínica.
    """
    return base_prompt

# --- INTERFAZ DE USUARIO (FRONTEND) ---

st.title("🏥 Soporte Tasy FLENI")

# 1. VERIFICAR ESTADO DE SESIÓN (¿Ya eligió rol?)
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. PANTALLA DE BIENVENIDA / SELECCIÓN (Si no hay rol definido)
if st.session_state.rol_usuario is None:
    st.markdown("### 👋 ¡Hola! Para poder ayudarte mejor, por favor indícame tu perfil:")
    st.info("Esta información nos ayuda a darte las rutas exactas de tu menú en Tasy.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Soy Enfermería 💉", use_container_width=True):
            st.session_state.rol_usuario = "Enfermería"
            st.session_state.messages.append({"role": "assistant", "content": "Hola colega de Enfermería. ¿En qué te trabaste? (Ej: '¿Cómo cargo un balance hídrico?', 'No veo mi paciente', 'Error al liberar signos vitales')."})
            st.rerun()
            
    with col2:
        if st.button("Soy Médico / Multi 🩺", use_container_width=True):
            st.session_state.rol_usuario = "Médico / Multi"
            st.session_state.messages.append({"role": "assistant", "content": "Hola Doctor/a o Licenciado/a. Estoy listo para ayudarte con Evoluciones, Informe Final o Agenda. ¿Cuál es tu consulta?"})
            st.rerun()

# 3. PANTALLA DE CHAT (Solo si ya eligió rol)
else:
    # Barra lateral con utilidades
    with st.sidebar:
        st.write(f"Perfil actual: **{st.session_state.rol_usuario}**")
        if st.button("Cambiar de Perfil"):
            st.session_state.rol_usuario = None
            st.session_state.messages = []
            st.rerun()
        st.divider()
        st.caption("Admin: Descargar reporte de consultas")
        # Aquí podrías poner un botón para descargar el CSV si eres admin

    # Mostrar historial
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input de usuario
    if prompt := st.chat_input("Escribe tu duda sobre Tasy aquí..."):
        
        # Mostrar mensaje usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Procesar respuesta (SIMULACIÓN DE LLM)
        with st.chat_message("assistant"):
            with st.spinner("Analizando manuales y rutas..."):
                
                # AQUI CONECTARIAS TU LLM REAL (OpenAI, etc)
                # Usando st.session_state.rol_usuario para filtrar el contexto
                
                # Respuesta Mockup Inteligente basada en tus documentos
                respuesta_texto = ""
                
                # Ejemplo de lógica de respuesta basada en tus manuales:
                if "informe final" in prompt.lower() and st.session_state.rol_usuario == "Médico / Multi":
                    respuesta_texto = "Para realizar el **Informe Final**:\n\n1. Ve a la función **Central de Informes**.\n2. Asegúrate que el estatus sea **Realizado**[cite: 324].\n3. Haz clic derecho > **Ejecutar** > **Incluir interpretación PDF**[cite: 325].\n\n**Nota cultural:** A diferencia del sistema anterior, aquí debes liberar manualmente la interpretación para que se pueda enviar por mail."
                
                elif "balance" in prompt.lower() and st.session_state.rol_usuario == "Enfermería":
                    respuesta_texto = "Para el **Balance Hídrico**:\n\n1. Ve a APAP o Balance Hídrico > Solapa **Ingresos y Egresos**[cite: 109].\n2. Clic en **Añadir**.\n3. Selecciona el ítem a la izquierda y usa la **flecha hacia la derecha** para asignarlo[cite: 113].\n4. Confirma en el pop-up.\n\nRecuerda que esto impacta automáticamente en la visualización del APAP."
                
                elif "sidca" in prompt.lower() or "historia vieja" in prompt.lower():
                    respuesta_texto = "Entiendo que necesites ver datos antiguos. Tasy permite consultar **SIDCA** sin salir de la pantalla:\n\n1. Haz clic derecho en el fondo blanco de la Historia Clínica.\n2. Selecciona **CES - Consulta Electrónica de Salud**.\n3. Esto abrirá la visualización de lo cargado en el sistema anterior."

                else:
                    respuesta_texto = f"Entiendo tu consulta sobre '{prompt}'. Como estás en perfil {st.session_state.rol_usuario}, te sugiero revisar que estés en el Sector correcto (esquina superior derecha)[cite: 4, 188]. ¿Podrías darme más detalles del error?"

                st.markdown(respuesta_texto)
                
                # LOGGING: Guardar la data para el equipo
                log_interaction(st.session_state.rol_usuario, prompt, respuesta_texto)

        st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})

