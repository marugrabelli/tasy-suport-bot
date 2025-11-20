import streamlit as st
import csv
import os
import pandas as pd
import json
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Flenisito - Soporte Tasy", page_icon="🏥", layout="wide")

# Archivos de Manuales (Verificación: Nombres correctos según tu GitHub)
LOG_FILE = "registro_consultas_flenisito.csv"
MANUAL_ENFERMERIA = "manual enfermeria (2).docx" 
MANUAL_MEDICOS = "Manual_Medicos.docx"
MANUAL_OTROS = "Manual Otros profesionales.docx"
KNOWLEDGE_FILE = "knowledge_base.json" # Archivo JSON con la estructura de respuestas

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
        # Muestra el error de sintaxis exacto para depuración
        st.error(f"❌ Error fatal: El archivo '{KNOWLEDGE_FILE}' no es un JSON válido.")
        st.code(f"Revisa la sintaxis (comas, llaves, corchetes). Detalle del error: {e}", language='text')
        return None

KNOWLEDGE_BASE = load_knowledge_base()

# Si la base de conocimiento no se pudo cargar, se detiene el script aquí
if KNOWLEDGE_BASE is None:
    st.stop()


# Definición de Tags (Las claves de 'response_key' deben coincidir con el JSON)
ENFERMERIA_TAGS = {
    # Grupo ADEP/Signos/Balance
    "Cargar Glucemia": {"color": "#FFC0CB", "query": "cargar glucemia", "response_key": "response_template_adep_glucemia"},
    "Ver Glucemia": {"color": "#ADD8E6", "query": "ver glucemia", "response_key": "response_template_adep_glucemia"},
    "Cargar Signos Vitales": {"color": "#90EE90", "query": "cargar signos vitales", "response_key": "response_template_signos_vitales"},
    "Ver Signos Vitales": {"color": "#87CEFA", "query": "ver signos vitales", "response_key": "response_template_signos_vitales"},
    "Balance por Turno": {"color": "#F08080", "query": "balance por turno", "response_key": "response_template_balance_hidrico"},
    "Balance por Día": {"color": "#FFA07A", "query": "balance por dia", "response_key": "response_template_balance_hidrico"},
    "Adm. Medicación si Dolor": {"color": "#DDA0DD", "query": "adm medicación si dolor", "response_key": "response_template_adep_med"},
    
    # Grupo Dispositivos/Login/Pase
    "Agregar un Nuevo Catéter": {"color": "#FAFAD2", "query": "agregar un nuevo catéter", "response_key": "response_template_dispositivos"},
    "Retirar Catéter": {"color": "#B0C4DE", "query": "retirar catéter", "response_key": "response_template_dispositivos"},
    "Contraseña y Usuario NO Coinciden": {"color": "#AFEEEE", "query": "contraseña y usuario no coinciden", "response_key": "response_template_login"},
    "Pase de Guardia": {"color": "#FFDAB9", "query": "pase de guardia", "response_key": "response_template_resumen_electronico"},
    
    # Grupo Otros
    "Otros (Pendientes/Escalas)": {"color": "#20B2AA", "query": "otros temas enfermeria", "response_key": "response_template_pendientes_eval"},
}

# Tags Médico/a
MEDICOS_TAGS = {
    "Evolucionar": {"color": "#4682B4", "query": "evolucionar medico", "response_key": "response_template_nota_clinica"},
    "Cargar Antecedentes del Paciente": {"color": "#6A5ACD", "query": "cargar antecedentes", "response_key": "response_template_antecedentes_multi"},
    "Epicrisis / Informe Final": {"color": "#DC143C", "query": "epicrisis informe final", "response_key": "response_template_informe_final"},
}

# Tags Otros Profesionales
OTROS_TAGS = {
    "Cargar Informe Inicial": {"color": "#9ACD32", "query": "cargar informe inicial", "response_key": "response_template_ged"},
    "Cargar Informe Final": {"color": "#FF8C00", "query": "cargar informe final", "response_key": "response_template_informe_final"},
    "Evolucionar": {"color": "#48D1CC", "query": "evolucionar otros", "response_key": "response_template_nota_clinica"},
}

# Mapping para CSS: Se mantiene
COLOR_MAP = {
    "#FFC0CB": "tag-pink", "#ADD8E6": "tag-lightblue", "#90EE90": "tag-lightgreen", 
    "#87CEFA": "tag-skyblue", "#F08080": "tag-lightcoral", "#FFA07A": "tag-lightsalmon", 
    "#DDA0DD": "tag-thistle", "#FAFAD2": "tag-lightyellow", "#B0C4DE": "tag-slategray", 
    "#AFEEEE": "tag-turquoise", "#FFDAB9": "tag-peach", "#20B2AA": "tag-seafoam",
    
    # Colores Médico/Otros
    "#4682B4": "tag-steel-blue", "#6A5ACD": "tag-slate-blue", "#DC143C": "tag-crimson",
    "#9ACD32": "tag-yellow-green", "#FF8C00": "tag-dark-orange", "#48D1CC": "tag-medium-turquoise"
}


# Estilos CSS (Se mantiene)
st.markdown(f"""
    <style>
    .stChatMessage {{ border-radius: 10px; }}
    .stButton button {{ width: 100%; border-radius: 5px; }}
    h1 {{ color: #005490; }}
    h3 {{ color: #005490; }}
    
    /* Clase para reducir el tamaño de letra del pie de página */
    .footer-content {{
        font-size: 0.9em;
        opacity: 0.9;
    }}
    /* Estilo para destacar el botón de descarga del manual */
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
    
    /* Estilos para los tags compactos */
    div[data-testid*="stHorizontalBlock"] > div[data-testid*="stVerticalBlock"] > div[data-testid*="column"] > div {{
        padding: 5px 2px;
    }}
    
    div[data-testid*="column"] > button {{
        /* Estilo general del botón del tag */
        margin-bottom: 8px;
        color: #333333 !important; /* Texto oscuro para contraste */
        font-weight: bold;
        border: 1px solid #ddd;
        /* Reducir el tamaño de fuente y padding del botón para hacerlo más compacto */
        font-size: 0.9em; 
        padding-top: 5px;
        padding-bottom: 5px;
        height: 100%;
    }}
    
    /* Generación dinámica de clases de colores */
    {
        "".join([
            f".{cls} button {{ background-color: {hex_color}; border-color: {hex_color}; }}"
            for hex_color, cls in COLOR_MAP.items()
        ])
    }

    /* Estilos para los botones de navegación (Volver / Dejar mensaje) */
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
            # NOTA: En el log, solo guardamos el texto de la respuesta, no el Markdown completo
            writer.writerow([now.date(), now.strftime("%H:%M:%S"), rol, pregunta, "Respuesta cargada desde JSON"]) 
    except Exception as e:
        pass

# Función para mostrar los botones de tags según el perfil (Se mantiene)
def show_tags(tag_list, columns_count, title):
    st.markdown(f"### 🔍 {title}")
    
    cols = st.columns(columns_count)
    
    for i, (label, data) in enumerate(tag_list.items()):
        
        # Mapea el color del tag a la clase CSS
        hex_color = data['color']
        css_class = COLOR_MAP[hex_color]
        button_key = f"tag_{label.replace(' ', '_').replace('/', '_').replace('.', '').lower()}"
        
        with cols[i % columns_count]:
            st.markdown(
                f'<div class="{css_class}">', 
                unsafe_allow_html=True
            )
            # El botón de Streamlit se renderiza dentro del div coloreado
            if st.button(label, key=button_key, use_container_width=True):
                # Al hacer clic, se establece la clave de respuesta y se rerenderiza
                st.session_state.response_key = data['response_key']
                st.session_state.last_prompt = data['query'] # Guarda el prompt para el log
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# Función para renderizar el pie de página (Manual, Avisos y Dudas) - Se mantiene
def render_footer():
    """Muestra el separador, el botón de descarga y el bloque de avisos."""
    st.markdown("---")
    
    # Botón de descarga 
    if "manual_file" in st.session_state and os.path.exists(st.session_state.manual_file):
        with open(st.session_state.manual_file, "rb") as f:
            st.download_button(
                label=f"📥 Descargar **{st.session_state.manual_label}**",
                data=f,
                file_name=os.path.basename(st.session_state.manual_file),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"descarga_{datetime.now().timestamp()}"
            )
    
    # Contenido del pie de página con tamaño de letra reducido
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


# Función para mostrar los botones de navegación al final de la respuesta (Se mantiene)
def show_navigation_buttons(rol):
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    
    col_back, col_msg = st.columns(2)
    
    # Lógica de "Volver a Escribir Consulta" (o Volver a Tags si es Enfermería)
    if rol == "Enfermería" and st.session_state.conversation_step != "free_input_after_msg":
        # Si es Enfermería y no viene de haber escrito un mensaje libre recién, vuelve a tags
        back_label = "💉 Volver a Opciones de Enfermería"
        target_step = "tags"
    elif rol in ["Médico", "Otros profesionales"] or st.session_state.conversation_step == "free_input_after_msg":
        # Si es Médico/Otros o si Enfermería acaba de escribir un mensaje libre, va a free_input
        back_label = "⬅️ Volver a Escribir una Consulta"
        target_step = "free_input"
    else:
        # Caso por defecto, volvemos a la última acción de tags/free_input
        back_label = "⬅️ Volver al menú anterior"
        target_step = "tags" # Default a tags si no hay otra información
        
    
    with col_back:
        if st.button(back_label, key="nav_back_unified", use_container_width=True):
            st.session_state.conversation_step = target_step
            st.session_state.response_key = None
            st.session_state.last_prompt = None
            st.rerun()

    # Botón 2: Dejar mensaje (Cambia al modo de input libre y notifica)
    with col_msg:
        if st.button("💬 No encontré respuesta (Dejar mensaje)", key="nav_leave_msg", use_container_width=True):
            st.session_state.conversation_step = "free_input_after_msg" # Nuevo estado para notificar
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
    # Mapea el rol interno de Streamlit al perfil del JSON
    if user_profile == "Enfermería":
        json_profile = "Hospitalización Enfermería"
    elif user_profile in ["Médico", "Otros profesionales"]:
        json_profile = "Hospitalización Multiprofesional"
    else:
        json_profile = user_profile # fallback
    
    path = template_data['path_to_item'].get(json_profile)
    if not path:
        path = "Ruta no especificada. Revisa la documentación."

    response += f"**Perfil {user_profile}**: {path}\n\n"
    
    # --- QUÉ PUEDO HACER (Acciones) ---
    response += f"### ✅ Acciones Clave\n"
    for action in template_data.get('actions', []):
        response += f"* {action}\n"
    response += "\n"

    # --- ERRORES Y SOLUCIONES ---
    # Iterar sobre la lista de errores (maneja el formato de lista de errores)
    if template_data.get('possible_errors'):
        response += f"### ⚠️ Posibles Errores y Soluciones\n"
        for error_block in template_data['possible_errors']:
            # Puede haber múltiples errores y soluciones dentro de la lista
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
    
    # --- FOOTER / MENSAJE FINAL ---
    response += "---\n"
    response += f"*{template_data.get('footer', '¿Deseas consultar otro tema o regresar al menú anterior?')}*\n"
    
    return response


# --- 4. MOTOR DE BÚSQUEDA ---
# Ahora mapea la consulta libre a las claves de templates del JSON
def buscar_solucion(consulta, rol):
    """Busca una solución basada en el texto libre, mapeando a una clave de template JSON."""
    q = consulta.lower()
    
    template_key = None

    # Mapeo de búsqueda libre a claves de respuesta JSON
    if any(x in q for x in ["contraseña", "usuario", "no veo paciente", "perfil", "login"]): 
        template_key = "response_template_login"
    if any(x in q for x in ["pase de guardia", "resumen", "cama", "sector", "navegacion"]): 
        template_key = "response_template_resumen_electronico"
    if any(x in q for x in ["sidca", "historia vieja", "anterior", "ces"]): 
        template_key = "response_template_sidca"

    # Enfermería (Mapeo a claves JSON específicas)
    if rol == "Enfermería":
        if any(x in q for x in ["signos", "vitales", "presion", "temperatura", "apap", "respiratoria"]): template_key = "response_template_signos_vitales"
        if any(x in q for x in ["balance", "hidrico", "ingreso", "egreso", "liquido"]): template_key = "response_template_balance_hidrico"
        if any(x in q for x in ["adep", "administrar", "medicacion", "droga", "glucemia", "revertir"]): template_key = "response_template_adep_med"
        if any(x in q for x in ["dispositivo", "sonda", "via", "cateter", "equipo", "rotar"]): template_key = "response_template_dispositivos"
        if any(x in q for x in ["pendiente", "tarea", "evaluacion", "escala", "score", "otros temas"]): template_key = "response_template_pendientes_eval"
    
    # Médico / Otros Profesionales
    if rol in ["Médico", "Otros profesionales"]:
        if any(x in q for x in ["evolucionar", "nota", "escribir", "duplicar", "plantilla"]): template_key = "response_template_nota_clinica"
        if any(x in q for x in ["antecedentes", "cargar antecedentes"]): template_key = "response_template_antecedentes_multi"
        if any(x in q for x in ["informe final", "epicrisis", "cargar informe"]): template_key = "response_template_informe_final"
        if any(x in q for x in ["cargar informe inicial", "ged", "documento"]): template_key = "response_template_ged"

    if template_key and KNOWLEDGE_BASE:
        template_data = KNOWLEDGE_BASE['response_templates'].get(template_key)
        if template_data:
            return render_response(template_data, rol)
    
    # Default si no encuentra en modo libre
    return "⚠️ No encontré un tema exacto para esa consulta. Te sugiero usar las opciones guiadas o revisar los manuales descargables."


# --- 5. INTERFAZ DE USUARIO ---

st.title("🏥 Flenisito")
st.markdown("**Tu Asistente Virtual para Tasy en FLENI**")

# Inicialización de Estados de Sesión (Se mantiene)
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

# LÓGICA DE BARRA LATERAL (SETTINGS Y ACCIONES) (Se mantiene)
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
    # Muestra imagen si existe
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
            st.session_state.conversation_step = "tags" # Va a la nube de tags
            st.rerun()
            
    with col2:
        if st.button("🩺 Soy **Médico/a**", key="btn_medico"):
            st.session_state.rol_usuario = "Médico"
            st.session_state.manual_file = MANUAL_MEDICOS
            st.session_state.manual_label = "Manual de Médicos Completo"
            st.session_state.messages.append({"role": "assistant", "content": "Hola Doctor/a. Por favor, selecciona el tema o escribe tu consulta:"})
            st.session_state.conversation_step = "tags" # Va a la nube de tags
            st.rerun()

    with col3:
        if st.button("👥 **Otros profesionales**", key="btn_otros"):
            st.session_state.rol_usuario = "Otros profesionales"
            st.session_state.manual_file = MANUAL_OTROS
            st.session_state.manual_label = "Manual de Otros Profesionales Completo"
            st.session_state.messages.append({"role": "assistant", "content": "¡Bienvenido/a! Por favor, selecciona el tema o ingresa tu consulta:"})
            st.session_state.conversation_step = "tags" # Va a la nube de tags
            st.rerun()

# --- 2. MOSTRAR HISTORIAL (Se mantiene) ---
if st.session_state.rol_usuario is not None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 3. FLUJO GUIADO POR TAGS (Enfermería, Médico, Otros) (Se mantiene) ---
if st.session_state.conversation_step == "tags":
    
    current_rol = st.session_state.rol_usuario
    
    if current_rol == "Enfermería":
        show_tags(ENFERMERIA_TAGS, 3, "Temas Específicos de Enfermería")
    elif current_rol == "Médico":
        show_tags(MEDICOS_TAGS, 3, "Temas Frecuentes de Médicos")
    elif current_rol == "Otros profesionales":
        show_tags(OTROS_TAGS, 3, "Temas Frecuentes de Otros Profesionales")
    
    # Opciones para el usuario (si elige escribir, se pasa a modo libre)
    st.markdown("---")
    prompt = st.chat_input("O escribe directamente aquí 'Otros' o tu consulta...")
    
    if prompt:
        st.session_state.conversation_step = "free_input" 
        st.rerun()

# --- 4. MOSTRAR RESPUESTA ESTRUCTURADA POR TAG ---
elif st.session_state.response_key is not None:
    
    key = st.session_state.response_key
    prompt_from_tag = st.session_state.last_prompt
    
    # 1. Renderiza el prompt del usuario (simulado)
    if prompt_from_tag:
        with st.chat_message("user"):
            st.markdown(prompt_from_tag.capitalize())
        st.session_state.messages.append({"role": "user", "content": prompt_from_tag})
    
    # 2. Renderiza la respuesta del bot usando la función de renderizado del JSON
    with st.chat_message("assistant"):
        with st.spinner("Flenisito está buscando la solución..."):
            
            template_data = KNOWLEDGE_BASE['response_templates'].get(key)
            respuesta_core = render_response(template_data, st.session_state.rol_usuario)
            st.markdown(respuesta_core, unsafe_allow_html=True) # Usar unsafe para la renderización

            # 3. Pie de página y Navegación
            render_footer() 
            show_navigation_buttons(st.session_state.rol_usuario)

            # 4. Log y Mensajes de Sesión
            if prompt_from_tag:
                log_interaction(st.session_state.rol_usuario, prompt_from_tag, key) # Loguea la clave del template
                st.session_state.messages.append({"role": "assistant", "content": respuesta_core})
                st.session_state.response_key = None # Finaliza el procesamiento de la respuesta
            st.rerun() # Rerun para asegurar la limpieza de estados y los botones

# --- 5. MODO LIBRE (FREE INPUT) ---
elif st.session_state.conversation_step in ["free_input", "viewing_response", "free_input_after_msg"]:
    
    # Si viene del estado de "dejar mensaje", mostramos la caja de input de chat
    if st.session_state.conversation_step in ["free_input", "free_input_after_msg"]:
        prompt = st.chat_input("Escribe tu consulta aquí...")
        
    # Si viene de una respuesta, solo mostramos los botones de navegación y no el chat_input
    else: # viewing_response
        prompt = None 
        
    # 5.1 Si hay un prompt nuevo (escribió)
    if prompt:
        # 1. Añade el prompt al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. RESPUESTA DEL BOT (Busca en la base de conocimiento y renderiza)
        with st.chat_message("assistant"):
            with st.spinner("Flenisito está buscando la solución..."):
                
                respuesta_core = buscar_solucion(prompt, st.session_state.rol_usuario)
                st.markdown(respuesta_core, unsafe_allow_html=True)
                
                # 3. Pie de página y Navegación
                render_footer() 
                show_navigation_buttons(st.session_state.rol_usuario)

                # 4. Log y Mensajes de Sesión
                log_interaction(st.session_state.rol_usuario, prompt, respuesta_core[:50] + "...") # Loguea los primeros 50 caracteres
                st.session_state.messages.append({"role": "assistant", "content": respuesta_core})
                st.session_state.conversation_step = "viewing_response" 
                st.rerun()

    # 5.2 Si estamos en viewing_response (no hay prompt, solo se renderizan los botones)
    elif st.session_state.conversation_step == "viewing_response":
        # Se asegura de que el pie de página se muestre antes de los botones, incluso sin un prompt nuevo
        with st.chat_message("assistant"):
             # Simula una respuesta vacía o regenera la última
             st.markdown("") 
             render_footer()
             show_navigation_buttons(st.session_state.rol_usuario)
