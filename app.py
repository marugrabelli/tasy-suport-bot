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
MANUAL_MEDICOS = "Manual_Medicos.docx"
MANUAL_OTROS = "Manual Otros profesionales.docx"
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
        # Muestra el error de sintaxis exacto para depuración
        st.error(f"❌ Error fatal: El archivo '{KNOWLEDGE_FILE}' no es un JSON válido.")
        st.code(f"Revisa la sintaxis (comas, llaves, corchetes). Detalle del error: {e}", language='text')
        return None

KNOWLEDGE_BASE = load_knowledge_base()

# Si la base de conocimiento no se pudo cargar, se detiene el script aquí
if KNOWLEDGE_BASE is None:
    st.stop()


# Definición de Tags (¡CORREGIDOS Y RE-MAPEDOS!)
ENFERMERIA_TAGS = {
    # 1. Cargar y Ver Glucemia -> Glucemia
    "Cargar Glucemia": {"color": "#FFC0CB", "query": "cargar glucemia", "response_key": "response_template_adep_glucemia"},
    "Ver Glucemia": {"color": "#ADD8E6", "query": "ver glucemia", "response_key": "response_template_adep_glucemia"},
    # 2. Signos Vitales -> SV (Carga) / APAP (Ver)
    "Cargar Signos Vitales": {"color": "#90EE90", "query": "cargar signos vitales", "response_key": "response_template_dispositivos"}, # Asumo que Signos Vitales (registro) requiere un nuevo template. Uso Dispositivos temporalmente.
    "Ver Signos Vitales/APAP": {"color": "#87CEFA", "query": "ver signos vitales/apap", "response_key": "response_template_signos_vitales"}, # Mapeado a APAP (Visualización)
    # 3. Balance Hídrico
    "Balance por Turno/Día": {"color": "#F08080", "query": "balance hidrico", "response_key": "response_template_balance_hidrico"},
    # 4. Adm. Medicación -> Sin información, mapeado a ADEP Glucemia por flujo.
    "Adm. Medicación": {"color": "#DDA0DD", "query": "administración de medicación", "response_key": "response_template_adep_glucemia"}, 
    
    # 5. Agregar/Retirar Catéter -> Unificado a Dispositivos
    "Agregar/Retirar Catéter": {"color": "#FAFAD2", "query": "gestión de catéter", "response_key": "response_template_dispositivos"},
    # 6. Contraseña y Usuario -> Login
    "Contraseña y Usuario NO Coinciden": {"color": "#AFEEEE", "query": "problemas de login", "response_key": "response_template_login"},
    # 7. Pase de Guardia -> Resumen Electrónico
    "Pase de Guardia/Resumen": {"color": "#FFDAB9", "query": "pase de guardia", "response_key": "response_template_resumen_electronico"},
    
    # 8. Evaluaciones/Escalas (Nombre y mapeo corregido)
    "Evaluaciones / Escalas": {"color": "#20B2AA", "query": "evaluaciones y escalas", "response_key": "response_template_evaluaciones"},
}

MEDICOS_TAGS = {
    "Evolucionar (Nota Clínica)": {"color": "#4682B4", "query": "evolucionar medico", "response_key": "response_template_nota_clinica"}, 
    "Cargar Antecedentes": {"color": "#6A5ACD", "query": "cargar antecedentes", "response_key": "response_template_nota_clinica"}, 
    "Epicrisis / Informe Final": {"color": "#DC143C", "query": "epicrisis informe final", "response_key": "response_template_informe_final"}, 
    "Consultar Evaluaciones": {"color": "#9ACD32", "query": "consultar evaluaciones", "response_key": "response_template_evaluaciones"}, 
}

OTROS_TAGS = {
    "Cargar Documentos (GED)": {"color": "#9ACD32", "query": "cargar informe inicial", "response_key": "response_template_ged"}, 
    "Cargar Informe Final": {"color": "#FF8C00", "query": "cargar informe final", "response_key": "response_template_informe_final"}, 
    "Evolucionar (Nota Clínica)": {"color": "#48D1CC", "query": "evolucionar otros", "response_key": "response_template_nota_clinica"}, 
    "Realizar Evaluaciones": {"color": "#48D1CC", "query": "realizar evaluaciones", "response_key": "response_template_evaluaciones"}, 
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


# Estilos CSS (Corregido para forzar el color de fondo y borde)
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
    /* ... otros estilos se mantienen ... */
    
    div[data-testid*="column"] > button {{
        margin-bottom: 8px;
        font-weight: bold;
        border: 1px solid #ddd;
        font-size: 0.9em; 
        padding-top: 5px;
        padding-bottom: 5px;
        height: 100%;
    }}
    
    {
        "".join([
            # Se fuerza color de fondo y borde para los tags
            f".{cls} button {{ background-color: {hex_color}; border-color: {hex_color}; }}"
            for hex_color, cls in COLOR_MAP.items()
        ])
    }
    
    /* Aseguramos que el texto del botón sea negro para contraste y eliminamos el color base del selector general */
    .tag-pink button, .tag-lightblue button, .tag-lightgreen button, .tag-skyblue button, 
    .tag-lightcoral button, .tag-lightsalmon button, .tag-thistle button, .tag-lightyellow button, 
    .tag-slategray button, .tag-turquoise button, .tag-peach button, .tag-seafoam button,
    .tag-steel-blue button, .tag-slate-blue button, .tag-crimson button, .tag-yellow-green button, 
    .tag-dark-orange button, .tag-medium-turquoise button {{
        color: black !important;
        border-color: #333333 !important; 
    }}

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
            log_response = respuesta if len(respuesta) < 100 else respuesta[:100] + "..."
            writer.writerow([now.date(), now.strftime("%H:%M:%S"), rol, pregunta, log_response]) 
    except Exception as e:
        pass

def show_tags(tag_list, columns_count, title):
    st.markdown(f"### 🔍 {title}")
    
    cols = st.columns(columns_count)
    
    # Se eliminan los tags "Agregar un Nuevo Catéter" y "Retirar Catéter" ya que están unificados
    # La lista de tags_enfermeria debe ser actualizada en el JSON
    
    for i, (label, data) in enumerate(tag_list.items()):
        
        hex_color = data['color']
        css_class = COLOR_MAP[hex_color]
        button_key = f"tag_{label.replace(' ', '_').replace('/', '_').replace('.', '').lower()}"
        
        with cols[i % columns_count]:
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
    """Muestra el separador, el botón de descarga y el bloque de avisos."""
    st.markdown("---")
    
    if "manual_file" in st.session_state and os.path.exists(st.session_state.manual_file):
        with open(st.session_state.manual_file, "rb") as f:
            st.download_button(
                label=f"📥 Descargar **{st.session_state.manual_label}**",
                data=f,
                file_name=os.path.basename(st.session_state.manual_file),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"descarga_{datetime.now().timestamp()}"
            )
    
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
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    
    col_back, col_msg = st.columns(2)
    
    # Lógica de Navegación Corregida
    target_step = "tags"
    if rol == "Enfermería":
        back_label = "💉 Volver a Opciones de Enfermería"
    elif rol == "Médico":
        back_label = "🩺 Volver a Opciones de Médicos"
    else: # Otros profesionales
        back_label = "👥 Volver a Opciones"
    
    # Caso especial: Si estamos en la pantalla de "Dejar mensaje", ajustamos la etiqueta y el destino
    if st.session_state.conversation_step == "free_input_after_msg":
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
        return "⚠️ Error al cargar la plantilla de respuesta o clave no encontrada."

    response = ""
    # --- TÍTULO ---
    response += f"## {template_data['title']}\n"
    response += "---\n"

    # --- DESCRIPCIÓN ---
    response += f"### 💡 Descripción\n"
    response += f"{template_data['description']}\n\n"

    # --- CÓMO LLEGAR ---
    response += f"### 🗺️ ¿Cómo llego?\n"
    if user_profile == "Enfermería":
        json_profile = "Hospitalización Enfermería"
    elif user_profile in ["Médico", "Otros profesionales"]:
        json_profile = "Hospitalización Multiprofesional"
    else:
        json_profile = user_profile 
    
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
    if video and video.get('url') != '#':
        response += f"### 🎥 Video\n"
        response += f"[{video['title']}]({video['url']})\n\n"
    
    # --- FOOTER / MENSAJE FINAL ---
    # Se elimina el footer de la plantilla y se usa el genérico de la función render_footer()
    
    return response


# --- 4. MOTOR DE BÚSQUEDA (Corregido para evitar duplicidad de "Dispositivos") ---
def buscar_solucion(consulta, rol):
    """Busca una solución basada en el texto libre, mapeando a una clave de template JSON."""
    q = consulta.lower()
    
    template_key = None
    
    # ORDEN DE IMPORTANCIA: Temas de acceso
    if any(x in q for x in ["contraseña", "usuario", "login", "perfil"]): 
        template_key = "response_template_login"
        
    # ORDEN DE IMPORTANCIA: Temas Médicos/Multi
    if rol in ["Médico", "Otros profesionales"]:
        if any(x in q for x in ["evolucionar", "nota", "plantilla"]): template_key = "response_template_nota_clinica"
        if any(x in q for x in ["informe final", "epicrisis"]): template_key = "response_template_informe_final"
        if any(x in q for x in ["ged", "documento"]): template_key = "response_template_ged"
        if any(x in q for x in ["evaluacion", "escala"]): template_key = "response_template_evaluaciones"
        if any(x in q for x in ["pase de guardia", "resumen"]): template_key = "response_template_resumen_electronico"
    
    # ORDEN DE IMPORTANCIA: Temas de Enfermería
    if rol == "Enfermería":
        if any(x in q for x in ["glucemia", "glucosa", "adep", "administrar medicacion"]): template_key = "response_template_adep_glucemia"
        if any(x in q for x in ["balance", "hidrico", "ingreso", "egreso"]): template_key = "response_template_balance_hidrico"
        if any(x in q for x in ["cateter", "dispositivo", "sonda", "via"]): template_key = "response_template_dispositivos"
        if any(x in q for x in ["signos", "vitales", "apap"]): template_key = "response_template_signos_vitales"
        if any(x in q for x in ["evaluacion", "escala"]): template_key = "response_template_evaluaciones"
        if any(x in q for x in ["pase de guardia", "resumen"]): template_key = "response_template_resumen_electronico"
    
    # Si la búsqueda libre NO encontró un tema específico de enfermería/multi, pero sí encontró un tema genérico
    if template_key is None:
        if any(x in q for x in ["sidca", "historia vieja", "anterior", "ces"]): 
            template_key = "response_template_dispositivos" # Se mantiene como placeholder

    if template_key and KNOWLEDGE_BASE:
        template_data = KNOWLEDGE_BASE['response_templates'].get(template_key)
        if template_data:
            # Si el tag es genérico y el perfil es multiprofesional, usa la info del multi (ya resuelta arriba)
            return render_response(template_data, rol)
    
    return "⚠️ No encontré un tema exacto para esa consulta. Te sugiero usar las opciones guiadas o revisar los manuales descargables."


# --- 5. INTERFAZ DE USUARIO (El resto del código se mantiene) ---

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

# --- 3. FLUJO GUIADO POR TAGS (Se mantiene) ---
if st.session_state.conversation_step == "tags":
    
    current_rol = st.session_state.rol_usuario
    
    if current_rol == "Enfermería":
        show_tags(ENFERMERIA_TAGS, 3, "Temas Específicos de Enfermería")
    elif current_rol == "Médico":
        show_tags(MEDICOS_TAGS, 3, "Temas Frecuentes de Médicos")
    elif current_rol == "Otros profesionales":
        show_tags(OTROS_TAGS, 3, "Temas Frecuentes de Otros Profesionales")
    
    st.markdown("---")
    prompt = st.chat_input("O escribe directamente aquí 'Otros' o tu consulta...")
    
    if prompt:
        st.session_state.conversation_step = "free_input" 
        st.rerun()

# --- 4. MOSTRAR RESPUESTA ESTRUCTURADA POR TAG (LÓGICA DE NAVEGACIÓN CORREGIDA) ---
elif st.session_state.response_key is not None:
    
    key = st.session_state.response_key
    prompt_from_tag = st.session_state.last_prompt
    
    if prompt_from_tag:
        with st.chat_message("user"):
            st.markdown(prompt_from_tag.capitalize())
        st.session_state.messages.append({"role": "user", "content": prompt_from_tag})
    
    with st.chat_message("assistant"):
        with st.spinner("Flenisito está buscando la solución..."):
            
            template_data = KNOWLEDGE_BASE['response_templates'].get(key)
            respuesta_core = render_response(template_data, st.session_state.rol_usuario)
            st.markdown(respuesta_core, unsafe_allow_html=True)

            render_footer() 
            show_navigation_buttons(st.session_state.rol_usuario)

            if prompt_from_tag:
                log_interaction(st.session_state.rol_usuario, prompt_from_tag, key)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_core})
                st.session_state.response_key = None
                st.session_state.conversation_step = "tags" 
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

                log_interaction(st.session_state.rol_usuario, prompt, respuesta_core[:100] + "...")
                st.session_state.messages.append({"role": "assistant", "content": respuesta_core})
                st.session_state.conversation_step = "viewing_response" 
                st.rerun()

    elif st.session_state.conversation_step == "viewing_response":
        with st.chat_message("assistant"):
             if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
                 st.markdown(st.session_state.messages[-1]["content"], unsafe_allow_html=True)
             
             render_footer()
             show_navigation_buttons(st.session_state.rol_usuario)

