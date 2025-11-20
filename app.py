import streamlit as st
import csv
import os
import pandas as pd
import json
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Flenisito - Soporte Tasy", page_icon="🏥", layout="wide")

# Archivos de Manuales
LOG_FILE = "registro_consultas_flenisito.csv"
MANUAL_ENFERMERIA = "manual enfermeria (2).docx" 
MANUAL_MEDICOS = "Manual hospitalizacion multi.docx" 
MANUAL_OTROS = "Manual hospitalizacion multi.docx" 
KNOWLEDGE_FILE = "knowledge_base.json" 

# Cargar la Base de Conocimiento JSON
@st.cache_data(show_spinner=False)
def load_knowledge_base():
    """Carga la base de conocimiento desde el archivo JSON al iniciar."""
    try:
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"❌ Error fatal: El archivo '{KNOWLEDGE_FILE}' no fue encontrado. ¡Asegúrate de haberlo subido!")
        return None
    except json.JSONDecodeError as e:
        st.error(f"❌ Error fatal: El archivo '{KNOWLEDGE_FILE}' no es un JSON válido.")
        st.code(f"Revisa la sintaxis (comas, llaves, corchetes). Detalle del error: {e}", language='text')
        return None

KNOWLEDGE_BASE = load_knowledge_base()
if KNOWLEDGE_BASE is None:
    st.stop()


# Definición de Tags y Mappings
# Colores ajustados a tonos pastel más suaves:
ENFERMERIA_TAGS = {
    "Cargar Glucemia": {"color": "#FFC0CB", "query": "cargar glucemia", "response_key": "response_template_adep_glucemia"},
    "Ver Glucemia": {"color": "#AEC6E3", "query": "ver glucemia", "response_key": "response_template_adep_glucemia"},
    "Cargar Signos Vitales": {"color": "#B4E4A2", "query": "cargar signos vitales", "response_key": "response_template_signos_vitales"},
    "Ver Signos Vitales": {"color": "#98D8D8", "query": "ver signos vitales", "response_key": "response_template_signos_vitales"},
    "Balance por Turno": {"color": "#F0B6C0", "query": "balance por turno", "response_key": "response_template_balance_hidrico"},
    "Balance por Día": {"color": "#FFD699", "query": "balance por dia", "response_key": "response_template_balance_hidrico"},
    "Adm. Medicación si Dolor": {"color": "#D3BFE8", "query": "adm medicación si dolor", "response_key": "response_template_adep_med"},
    
    "Agregar un Nuevo Catéter": {"color": "#FFFFD8", "query": "agregar un nuevo catéter", "response_key": "response_template_dispositivos"},
    "Retirar Catéter": {"color": "#C0D9E8", "query": "retirar catéter", "response_key": "response_template_dispositivos"},
    "Contraseña y Usuario NO Coinciden": {"color": "#C4E8D6", "query": "contraseña y usuario no coinciden", "response_key": "response_template_login"},
    "Pase de Guardia": {"color": "#FFE9BF", "query": "pase de guardia", "response_key": "response_template_resumen_electronico"},
    
    "Otros (Pendientes/Escalas)": {"color": "#A0D4E4", "query": "otros temas enfermeria", "response_key": "response_template_evaluaciones"},
}

MEDICOS_TAGS = {
    "Evolucionar": {"color": "#A9CCE3", "query": "evolucionar medico", "response_key": "response_template_nota_clinica"},
    "Cargar Antecedentes del Paciente": {"color": "#B5A7D0", "query": "cargar antecedentes", "response_key": "response_template_antecedentes_multi"},
    "Epicrisis / Informe Final": {"color": "#EC7063", "query": "epicrisis informe final", "response_key": "response_template_informe_final"},
}

OTROS_TAGS = {
    "Cargar Informe Inicial": {"color": "#B8DB84", "query": "cargar informe inicial", "response_key": "response_template_ged"},
    "Cargar Informe Final": {"color": "#FFBB77", "query": "cargar informe final", "response_key": "response_template_informe_final"},
    "Evolucionar": {"color": "#A3E4D7", "query": "evolucionar otros", "response_key": "response_template_nota_clinica"},
}

# Mapping para CSS
COLOR_MAP = {
    # Nuevos colores pastel
    "#FFC0CB": "tag-pink", "#AEC6E3": "tag-softblue", "#B4E4A2": "tag-softgreen", 
    "#98D8D8": "tag-softcyan", "#F0B6C0": "tag-coral", "#FFD699": "tag-peach", 
    "#D3BFE8": "tag-lavender", "#FFFFD8": "tag-ivory", "#C0D9E8": "tag-sky", 
    "#C4E8D6": "tag-mint", "#FFE9BF": "tag-lightpeach", "#A0D4E4": "tag-sky-blue",
    
    # Colores Médico/Otros
    "#A9CCE3": "tag-steel-blue-soft", "#B5A7D0": "tag-slate-blue-soft", "#EC7063": "tag-crimson-soft",
    "#B8DB84": "tag-yellow-green-soft", "#FFBB77": "tag-dark-orange-soft", "#A3E4D7": "tag-medium-turquoise-soft"
}


# Estilos CSS (Se mantiene)
st.markdown(f"""
    <style>
    .stChatMessage {{ border-radius: 10px; }}
    .stButton button {{ width: 100%; border-radius: 5px; }}
    h1 {{ color: #005490; }}
    h3 {{ color: #005490; }}
    
    .footer-content {{
        font-size: 0.9em;
        opacity: 0.9;
    }}
    .stDownloadButton button {{
        border: 1px solid #005490;
        color: #005490;
        background-color: #f0f8ff;
        margin-bottom: 10px;
    }}
    .stDownloadButton button:hover {{
        background-color: #005490;
        color: white;
    }}
    
    div[data-testid*="stHorizontalBlock"] > div[data-testid*="stVerticalBlock"] > div[data-testid*="column"] > div {{
        padding: 5px 2px;
    }}
    
    div[data-testid*="column"] > button {{
        margin-bottom: 8px;
        color: #333333 !important; 
        font-weight: bold;
        border: 1px solid #ddd;
        font-size: 0.9em; 
        padding-top: 5px;
        padding-bottom: 5px;
        height: 100%;
    }}
    
    {
        "".join([
            # Aumento de Especificidad CSS: Apuntamos directamente al div que contiene la clase y usamos !important
            f"div.{cls} button {{ background-color: {hex_color} !important; border-color: {hex_color} !important; }}"
            for hex_color, cls in COLOR_MAP.items()
        ])
    }

    .nav-button-container button {{
        background-color: #f0f2f6;
        color: #005490 !important;
        border: 1px solid #005490;
        font-weight: 500;
        margin-top: 15px;
    }}
    .nav-button-container button:hover {{
        background-color: #005490;
        color: white !important;
    }}

    </style>
    """, unsafe_allow_html=True)


# --- 2. FUNCIONES DE BACKEND ---
def log_interaction(rol, pregunta, respuesta):
    file_exists = os.path.isfile(LOG_FILE)
    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Fecha", "Hora", "Rol", "Pregunta", "Respuesta_Bot"])
            now = datetime.now()
            writer.writerow([now.date(), now.strftime("%H:%M:%S"), rol, pregunta, "Respuesta cargada desde JSON"]) 
    except Exception as e:
        pass

def show_tags(tag_list, columns_count, title):
    st.markdown(f"### 🔍 {title}")
    
    cols = st.columns(columns_count) 
    
    for i, (label, data) in enumerate(tag_list.items()):
        
        hex_color = data['color']
        # Se obtiene el CSS class basado en el nuevo COLOR_MAP
        css_class = next((cls for color, cls in COLOR_MAP.items() if color == hex_color), "") 
        button_key = f"tag_{label.replace(' ', '_').replace('/', '_').replace('.', '').lower()}"
        
        with cols[i % columns_count]:
            # Se aplica la clase CSS al div contenedor del botón
            st.markdown(
                f'<div class="{css_class}">', 
                unsafe_allow_html=True
            )
            if st.button(label, key=button_key, use_container_width=True):
                st.session_state.response_key = data['response_key']
                st.session_state.last_prompt = data['query']
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


def render_footer():
    """Muestra el separador, el botón de descarga del manual y el bloque de avisos."""
    st.markdown("---")
    
    # Descarga del Manual (Requisito)
    if "manual_file" in st.session_state and os.path.exists(st.session_state.manual_file):
        with open(st.session_state.manual_file, "rb") as f:
            st.download_button(
                label=f"📥 Descargar **{st.session_state.manual_label}**",
                data=f,
                file_name=os.path.basename(st.session_state.manual_file),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"descarga_{datetime.now().timestamp()}"
            )
    
    # Bloque de soporte/contacto (Requisito: Mensaje final)
    with st.container():
        st.markdown('<div class="footer-content">', unsafe_allow_html=True)
        st.markdown("""
### 💡 Antes de llamar, ¡revisa estos puntos!

* **💻 Navegador Ideal:** Usa siempre **Google Chrome**.
* **🧹 Limpieza:** Si algo no carga, prueba a **limpiar la caché** (`Ctrl + H`).
* **👤 Perfil:** Verifica que tu **Log In** esté en el **establecimiento y perfil correcto** (Ej: Hospitalización Multi/Enfermería).
* **🔍 Zoom:** ¿Pantalla cortada? Ajusta el zoom: **`Ctrl + +`** (agrandar) o **`Ctrl + -`** (minimizar).

---
**¿Aún tienes dudas?**

* 🖋️ **Firmas Digitales:** Envía tu firma en **formato JPG (fondo blanco)** a **soportesidca@fleni.org.ar**.
* 📞 **Soporte Telefónico:** Llama al interno **5006**.
* 🎫 **Alta de Usuarios/VPN:** Deja un ticket en **solicitudes.fleni.org**.
""")
        st.markdown('</div>', unsafe_allow_html=True)


def show_navigation_buttons(rol):
    """Muestra los botones para volver al menú o dejar un mensaje (Requisito)."""
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    
    col_back, col_msg = st.columns(2)
    
    # Lógica para el botón de volver atrás
    if st.session_state.conversation_step == "tags":
        back_label = "💉 Volver a Opciones de Enfermería" if rol == "Enfermería" else "👥 Volver a Opciones Multiprofesionales"
        target_step = "tags"
    else:
        # Esto cubre "viewing_response" o "free_input_after_msg"
        back_label = "⬅️ Volver a Escribir una Consulta"
        target_step = "free_input"
        
    
    with col_back:
        if st.button(back_label, key="nav_back_unified", use_container_width=True):
            st.session_state.conversation_step = target_step
            st.session_state.response_key = None
            st.session_state.last_prompt = None
            st.rerun()

    with col_msg:
        if st.button("💬 No encontré respuesta (Dejar mensaje)", key="nav_leave_msg", use_container_width=True):
            st.session_state.conversation_step = "free_input_after_msg" 
            st.session_state.response_key = None
            st.session_state.last_prompt = None
            st.session_state.messages.append({"role": "assistant", "content": "Entendido. Por favor, describe tu problema con más detalle para que podamos ayudarte a encontrar la respuesta o derivar tu consulta al equipo de soporte."})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# --- 3. FUNCIÓN CLAVE DE RENDERIZADO (UX/Markdown) ---

def render_response(template_data, user_profile):
    """
    Genera la respuesta final en un formato amigable con UX (Markdown y Emojis)
    a partir de la plantilla JSON.
    """
    if not template_data:
        return "⚠️ Error al cargar la plantilla de respuesta."

    response = ""
    # --- TÍTULO ---
    response += f"## {template_data['title']}\n"
    response += "---\n"

    # --- DESCRIPCIÓN ---
    response += f"### 💡 Descripción\n"
    response += f"{template_data['description']}\n\n"

    # --- CÓMO LLEGAR ---
    response += f"### 🗺️ ¿Cómo llego?\n"
    # Usamos las claves de mapeo del JSON (sin tildes/eñes, como en el JSON)
    json_profile_enfermeria = "Hospitalizacion Enfermeria"
    json_profile_multi = "Hospitalizacion Multiprofesional"
    
    if user_profile == "Enfermería":
        path = template_data['path_to_item'].get(json_profile_enfermeria, "Ruta no especificada.")
    elif user_profile in ["Médico", "Otros profesionales"]:
        path = template_data['path_to_item'].get(json_profile_multi, "Ruta no especificada.")
    else:
        path = "Ruta no especificada."

    response += f"**Perfil {user_profile}**: {path}\n\n"
    
    # --- QUÉ PUEDO HACER (Acciones) ---
    response += f"### ✅ Acciones Clave\n"
    for action in template_data.get('actions', []):
        response += f"* {action}\n"
    response += "\n"

    # --- ERRORES Y SOLUCIONES ---
    if template_data.get('possible_errors'):
        response += f"### ⚠️ Posibles Errores y Soluciones\n"
        for error_block in template_data['possible_errors']:
            if error_block.get('error') and error_block.get('solution'):
                 response += f"* **Error**: {error_block['error']}\n"
                 response += f"  * **Solución**: {error_block['solution']}\n"
        response += "\n"

    # --- TIPS ---
    if template_data.get('tips'):
        response += f"### ✨ Tips del Experto\n"
        for tip in template_data['tips']:
            response += f"* {tip}\n"
        response += "\n"

    # --- VIDEO (Enlace Clickeable) ---
    video = template_data.get('video_link')
    if video:
        response += f"### 🎥 Video\n"
        response += f"[{video['title']}]({video['url']})\n\n"
    
    # --- FOOTER / MENSAJE FINAL (El footer se llama después de esta función) ---
    response += "---\n"
    response += f"*{template_data.get('footer', '¿Deseas consultar otro tema o regresar al menú anterior?')}*\n"
    
    return response


# --- 4. MOTOR DE BÚSQUEDA ---
def buscar_solucion(consulta, rol):
    """Busca una solución basada en el texto libre, mapeando a una clave de template JSON."""
    q = consulta.lower()
    
    template_key = None

    # Mapeo de búsqueda libre a claves de respuesta JSON (Globales)
    if any(x in q for x in ["contraseña", "usuario", "no veo paciente", "perfil", "login"]): 
        template_key = "response_template_login"
    if any(x in q for x in ["pase de guardia", "resumen", "cama", "sector", "navegacion"]): 
        template_key = "response_template_resumen_electronico"
    if any(x in q for x in ["sidca", "historia vieja", "anterior", "ces"]): 
        template_key = "response_template_sidca"

    # Enfermería (Lógica de prioridad para búsqueda libre)
    if rol == "Enfermería":
        # Glucemia
        if any(x in q for x in ["glucemia", "protocolo"]):
             template_key = "response_template_adep_glucemia"
        # Signos Vitales
        elif any(x in q for x in ["signos", "vitales", "presion", "temperatura", "apap", "respiratoria"]): 
            template_key = "response_template_signos_vitales"
        # Balance Hídrico
        elif any(x in q for x in ["balance", "hidrico", "ingreso", "egreso", "liquido"]): 
            template_key = "response_template_balance_hidrico"
        # ADEP (Medicamentos, dietas, etc., si no fue cubierto por glucemia)
        elif any(x in q for x in ["adep", "administrar", "medicacion", "droga", "revertir"]): 
            template_key = "response_template_adep_med"
        # Dispositivos
        elif any(x in q for x in ["dispositivo", "sonda", "via", "cateter", "equipo", "rotar"]): 
            template_key = "response_template_dispositivos"
        # Evaluaciones/Escalas
        elif any(x in q for x in ["pendiente", "tarea", "evaluacion", "escala", "score", "otros temas"]): 
            template_key = "response_template_evaluaciones"
    
    # Médico / Otros Profesionales
    if rol in ["Médico", "Otros profesionales"]:
        if any(x in q for x in ["evolucionar", "nota", "escribir", "duplicar", "plantilla"]): 
            template_key = "response_template_nota_clinica"
        if any(x in q for x in ["antecedentes", "cargar antecedentes"]): 
            template_key = "response_template_antecedentes_multi"
        if any(x in q for x in ["informe final", "epicrisis", "cargar informe"]): 
            template_key = "response_template_informe_final"
        if any(x in q for x in ["cargar informe inicial", "ged", "documento"]): 
            template_key = "response_template_ged"

    if template_key and KNOWLEDGE_BASE:
        template_data = KNOWLEDGE_BASE['response_templates'].get(template_key)
        if template_data:
            return render_response(template_data, rol)
    
    return "⚠️ No encontré un tema exacto para esa consulta. Te sugiero usar las opciones guiadas o revisar los manuales descargables."


# --- 5. INTERFAZ DE USUARIO ---

st.title("🏥 Flenisito")
st.markdown("**Tu Asistente Virtual para Tasy en FLENI**")

# Inicialización de Estados de Sesión
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "response_key" not in st.session_state:
    st.session_state.response_key = None
if "conversation_step" not in st.session_state:
    st.session_state.conversation_step = "onboarding"
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None

# LÓGICA DE BARRA LATERAL (Se mantiene)
if st.session_state.rol_usuario is not None:
    with st.sidebar:
        st.success(f"Perfil activo: **{st.session_state.rol_usuario}**")
        
        st.markdown("---")
        st.markdown("### 💡 Tips Rápidos")
        st.caption("1. **Liberar** = Publicar. **Guardar** = Borrador.")
        st.caption("2. ¿No ves pacientes? Revisa **Sector** y **Establecimiento**.") 
        st.caption("3. **SIDCA:** Clic derecho > CES.")
        st.markdown("---")

        if st.button("🔄 Cambiar de Perfil"):
            st.session_state.rol_usuario = None
            st.session_state.messages = []
            st.session_state.conversation_step = "onboarding"
            for key in ["manual_file", "manual_label", "response_key", "last_prompt"]:
                if key in st.session_state: del st.session_state[key]
            st.rerun()
        if st.button("🗑️ Borrar Chat"):
            st.session_state.messages = []
            st.rerun()
            
        st.markdown("---")
        with st.expander("🔐 Admin Logs"):
            clave = st.text_input("Contraseña:", type="password")
            if clave == "fleniadmin":
                if os.path.exists(LOG_FILE):
                    st.write("### Registro de Consultas")
                    df = pd.read_csv(LOG_FILE)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Aún no hay registros.")

# --- FLUJO PRINCIPAL ---

# 1. ONBOARDING (Se mantiene)
if st.session_state.conversation_step == "onboarding":
    # Muestra el logo o imagen de bienvenida si existe 
    if os.path.exists("image_39540a.png"):
        st.image("image_39540a.png", use_column_width="auto")
    elif os.path.exists("image_3950c3.png"):
        st.image("image_3950c3.png", use_column_width="auto")
    
    st.info("👋 ¡Hola! Soy Flenisito. Para ayudarte mejor, selecciona tu perfil:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💉 Soy **Enfermero/a**", key="btn_enfermeria"):
            st.session_state.rol_usuario = "Enfermería"
            st.session_state.manual_file = MANUAL_ENFERMERIA
            st.session_state.manual_label = "Manual de Enfermería Completo"
            st.session_state.messages.append({"role": "assistant", "content": "Hola colega. Por favor, selecciona el tema en el que necesitas ayuda a continuación:"})
            st.session_state.conversation_step = "tags"
            st.rerun()
            
    with col2:
        if st.button("🩺 Soy **Médico/a**", key="btn_medico"):
            st.session_state.rol_usuario = "Médico"
            st.session_state.manual_file = MANUAL_MEDICOS
            st.session_state.manual_label = "Manual de Médicos Completo"
            st.session_state.messages.append({"role": "assistant", "content": "Hola Doctor/a. Por favor, selecciona el tema o escribe tu consulta:"})
            st.session_state.conversation_step = "tags"
            st.rerun()

    with col3:
        if st.button("👥 **Otros profesionales**", key="btn_otros"):
            st.session_state.rol_usuario = "Otros profesionales"
            st.session_state.manual_file = MANUAL_OTROS
            st.session_state.manual_label = "Manual de Otros Profesionales Completo"
            st.session_state.messages.append({"role": "assistant", "content": "¡Bienvenido/a! Por favor, selecciona el tema o ingresa tu consulta:"})
            st.session_state.conversation_step = "tags"
            st.rerun()

# --- 2. MOSTRAR HISTORIAL (Se mantiene) ---
if st.session_state.rol_usuario is not None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 3. FLUJO GUIADO POR TAGS ---
if st.session_state.conversation_step == "tags":
    
    current_rol = st.session_state.rol_usuario
    
    # Se utiliza 4 columnas para compactar los botones
    if current_rol == "Enfermería":
        show_tags(ENFERMERIA_TAGS, 4, "Temas Específicos de Enfermería") 
    elif current_rol == "Médico":
        show_tags(MEDICOS_TAGS, 3, "Temas Frecuentes de Médicos")
    elif current_rol == "Otros profesionales":
        show_tags(OTROS_TAGS, 3, "Temas Frecuentes de Otros Profesionales")
    
    st.markdown("---")
    prompt = st.chat_input("O escribe directamente aquí 'Otros' o tu consulta...")
    
    if prompt:
        st.session_state.conversation_step = "free_input" 
        st.rerun()

# --- 4. MOSTRAR RESPUESTA ESTRUCTURADA POR TAG ---
elif st.session_state.response_key is not None:
    
    key = st.session_state.response_key
    prompt_from_tag = st.session_state.last_prompt
    
    # 1. Renderizar prompt del usuario
    if prompt_from_tag:
        with st.chat_message("user"):
            st.markdown(prompt_from_tag.capitalize())
        st.session_state.messages.append({"role": "user", "content": prompt_from_tag})
    
    # 2. Generar y renderizar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Flenisito está buscando la solución..."):
            
            template_data = KNOWLEDGE_BASE['response_templates'].get(key)
            respuesta_core = render_response(template_data, st.session_state.rol_usuario)
            
            # Renderiza la respuesta principal
            st.markdown(respuesta_core, unsafe_allow_html=True) 

            # Renderiza el footer (Manual, Tips, Contactos)
            render_footer() 
            
            # Renderiza los botones de navegación
            show_navigation_buttons(st.session_state.rol_usuario)

            # 3. Guardar la interacción y actualizar el estado
            if prompt_from_tag:
                log_interaction(st.session_state.rol_usuario, prompt_from_tag, key)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_core})
            
            # 4. Se borra la clave de respuesta y se pasa al estado de visualización
            st.session_state.response_key = None
            st.session_state.conversation_step = "viewing_response" 
            
            st.rerun() 

# --- 5. MODO LIBRE (FREE INPUT) ---
elif st.session_state.conversation_step in ["free_input", "viewing_response", "free_input_after_msg"]:
    
    if st.session_state.conversation_step in ["free_input", "free_input_after_msg"]:
        prompt = st.chat_input("Escribe tu consulta aquí...")
    else: 
        prompt = None 
        
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Flenisito está buscando la solución..."):
                
                respuesta_core = buscar_solucion(prompt, st.session_state.rol_usuario)
                st.markdown(respuesta_core, unsafe_allow_html=True)
                
                render_footer() 
                show_navigation_buttons(st.session_state.rol_usuario)

                log_interaction(st.session_state.rol_usuario, prompt, respuesta_core[:50] + "...")
                st.session_state.messages.append({"role": "assistant", "content": respuesta_core})
                st.session_state.conversation_step = "viewing_response" 
                st.rerun()

    elif st.session_state.conversation_step == "viewing_response":
        # Se asegura que los botones y footer se mantengan visibles tras el rerun.
        st.chat_input("Escribe tu consulta aquí...")
        render_footer()
        show_navigation_buttons(st.session_state.rol_usuario)

