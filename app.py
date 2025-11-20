import streamlit as st
import csv
import os
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Flenisito - Soporte Tasy", page_icon="🏥", layout="wide")

# Archivos de Manuales (Verificación: Nombres correctos según tu GitHub)
LOG_FILE = "registro_consultas_flenisito.csv"
MANUAL_ENFERMERIA = "manual enfermeria (2).docx" 
MANUAL_MEDICOS = "Manual_Medicos.docx"
MANUAL_OTROS = "Manual Otros profesionales.docx"

# Definición de Tags de Enfermería: Nombre exacto, Consulta que lanza, y Respuesta a mostrar
ENFERMERIA_TAGS = {
    # Grupo ADEP/Signos/Balance
    "Cargar Glucemia": {"color": "#FFC0CB", "query": "cargar glucemia", "response_key": "adep"},
    "Ver Glucemia": {"color": "#ADD8E6", "query": "ver glucemia", "response_key": "adep"},
    "Cargar Signos Vitales": {"color": "#90EE90", "query": "cargar signos vitales", "response_key": "signos vitales"},
    "Ver Signos Vitales": {"color": "#87CEFA", "query": "ver signos vitales", "response_key": "signos vitales"},
    "Balance por Turno": {"color": "#F08080", "query": "balance por turno", "response_key": "balance hidrico"},
    "Balance por Día": {"color": "#FFA07A", "query": "balance por dia", "response_key": "balance hidrico"},
    "Adm. Medicación si Dolor": {"color": "#DDA0DD", "query": "adm medicación si dolor", "response_key": "adep"},
    
    # Grupo Dispositivos/Login/Pase
    "Agregar un Nuevo Catéter": {"color": "#FAFAD2", "query": "agregar un nuevo catéter", "response_key": "dispositivos"},
    "Retirar Catéter": {"color": "#B0C4DE", "query": "retirar catéter", "response_key": "dispositivos"},
    "Contraseña y Usuario NO Coinciden": {"color": "#AFEEEE", "query": "contraseña y usuario no coinciden", "response_key": "login"},
    "Pase de Guardia": {"color": "#FFDAB9", "query": "pase de guardia", "response_key": "navegacion"},
    
    # Grupo Otros
    "Otros (Pendientes/Escalas)": {"color": "#20B2AA", "query": "otros temas enfermeria", "response_key": "pendientes_eval"},
}

# Tags Médico/a
MEDICOS_TAGS = {
    "Evolucionar": {"color": "#4682B4", "query": "evolucionar medico", "response_key": "nota clinica"},
    "Cargar Antecedentes del Paciente": {"color": "#6A5ACD", "query": "cargar antecedentes", "response_key": "antecedentes_multi"},
    "Epicrisis / Informe Final": {"color": "#DC143C", "query": "epicrisis informe final", "response_key": "informe final"},
}

# Tags Otros Profesionales
OTROS_TAGS = {
    "Cargar Informe Inicial": {"color": "#9ACD32", "query": "cargar informe inicial", "response_key": "ged"},
    "Cargar Informe Final": {"color": "#FF8C00", "query": "cargar informe final", "response_key": "informe final"},
    "Evolucionar": {"color": "#48D1CC", "query": "evolucionar otros", "response_key": "nota clinica"},
}

# Mapping para CSS: Se genera dinámicamente el mapping de color a clase
COLOR_MAP = {
    "#FFC0CB": "tag-pink", "#ADD8E6": "tag-lightblue", "#90EE90": "tag-lightgreen", 
    "#87CEFA": "tag-skyblue", "#F08080": "tag-lightcoral", "#FFA07A": "tag-lightsalmon", 
    "#DDA0DD": "tag-thistle", "#FAFAD2": "tag-lightyellow", "#B0C4DE": "tag-slategray", 
    "#AFEEEE": "tag-turquoise", "#FFDAB9": "tag-peach", "#20B2AA": "tag-seafoam",
    
    # Colores Médico/Otros
    "#4682B4": "tag-steel-blue", "#6A5ACD": "tag-slate-blue", "#DC143C": "tag-crimson",
    "#9ACD32": "tag-yellow-green", "#FF8C00": "tag-dark-orange", "#48D1CC": "tag-medium-turquoise"
}


# Estilos CSS
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
            writer.writerow([now.date(), now.strftime("%H:%M:%S"), rol, pregunta, respuesta])
    except Exception as e:
        pass

# Función para mostrar los botones de tags según el perfil
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


# Función para renderizar el pie de página (Manual, Avisos y Dudas)
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


# Función para mostrar los botones de navegación al final de la respuesta
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

# --- 3. BASE DE CONOCIMIENTO (TOTALMENTE LIMPIA DE CITES) ---
base_de_conocimiento = {
    # === TEMAS GENERALES ===
    "login": {
        "contenido": "### 🔐 Acceso y Login\n\n**Ruta:** URL: https://tasy.fleni.org.ar/#/login\n\n**⚠️ Solución a Errores Frecuentes (Contraseña / Usuario):**\n* **Verifica el Perfil:** Revisa la esquina superior derecha para confirmar que estás en el perfil correcto (Hospitalización Multi o Enfermería).\n* **Verifica el Sector:** Es obligatorio seleccionar el sector correspondiente para visualizar pacientes.\n* **Cerrar Sesión:** Haz clic siempre en 'Salir' (Logout)."
    },
    "navegacion": {
        "contenido": "### 🧭 Navegación y Búsqueda (Pase de Guardia)\n\n**Función:** La función Perspectiva Clínica permite ver el listado de camas.\n\n**Pase de Guardia:**\n* El **Resumen Electrónico** es el ítem ideal para el pase de guardia, ya que agrupa toda la información necesaria del paciente brevemente.\n* Para ingresar a la HCE, haz doble clic sobre el nombre del paciente."
    },
    "sidca": {
        "contenido": "### 🕰️ Consulta Histórica (SIDCA)\n\n**Pasos:**\n1. Desde cualquier parte de la HCE del paciente.\n2. Haz **clic derecho** en el fondo blanco de la pantalla.\n3. Selecciona **CES - Consulta Electrónica de Salud**.\n4. Esto te dirigirá a SIDCA para visualizar los registros cargados de ese paciente."
    },

    # === PERFIL ENFERMERÍA ===
    "signos vitales": {
        "contenido": "### 🩺 Signos Vitales y Parámetros Respiratorios (Cargar/Ver)\n\n**Ruta para Cargar:**\n* Solapa **Signos Vitales** > Botón **Añadir**.\n\n**Pasos Clave:**\n1. Rellena los campos y verifica la hora del control.\n2. **IMPORTANTE:** Marca la casilla **APAP** si quieres que el dato sea visible en la grilla general (Análisis de Parámetros Asistenciales).\n3. **Liberar** permite publicar en la historia clínica y ser visible para todos.\n\n**Visualización (Ver Signos):**\n* Puedes visualizar los datos previamente cargados mirando fecha, hora, y aplicando filtros."
    },
    "balance hidrico": {
        "contenido": "### 💧 Balance Hídrico (Por Turno / Día)\n\n**Ruta para Cargar:**\n* Solapa de **Ingresos y egresos**.\n\n**Pasos para Cargar:**\n1. Clic en **Añadir**.\n2. Selecciona el Grupo y Tipo (Ingresos o Egresos) y haz clic en la **Flecha Derecha (➡️)** para agregarlo.\n3. Ingresa el volumen y confirma con **Finalizar**.\n\n**Visualización:**\n* La solapa **Análisis de balance** muestra el detalle del balance total, por turno y el detalle de cada turno seleccionado."
    },
    "adep": {
        "contenido": "### 💊 ADEP (Glucemia y Medicación)\n\n**Rutas:**\n* **Medicamentos:** Ítem **ADEP** en el árbol lateral.\n* **Glucemia (Cargar/Ver):** Ítem **Exámenes y procedimientos** (Glucemia con protocolo).\n\n**Pasos (Administrar Medicación):**\n1. Busca el horario pendiente (lado derecho).\n2. **Clic derecho** > **Administrar / revertir evento**.\n3. Da OK para confirmar el registro.\n\n**Pasos (Cargar Glucemia):**\n1. En 'Exámenes y procedimientos', clic derecho e inicias el registro del valor de glucemia.\n2. Los valores de glucemia cargados en adep impactan en APAP y Signos Vitales."
    },
    "dispositivos": {
        "contenido": "### 💉 Dispositivos (Agregar y Retirar Catéteres/Vías)\n\n**Ruta:**\n* Ítem **Dispositivos/Equipos**.\n\n**Pasos (Agregar/Nuevo Catéter):**\n* Ve a 'Gráfico de dispositivos' > **Nuevo dispositivo**.\n* Elige el dispositivo y la fecha prevista o estimada de retiro o rotación.\n\n**Pasos (Retirar):**\n* Clic en **Acciones de dispositivo**.\n* Selecciona el dispositivo a retirar.\n* Justifica el motivo de retirada y haz clic en Ok."
    },
    "pendientes_eval": {
        "contenido": "### 📋 Pendientes de Enfermería y Evaluaciones/Escalas\n\n**Rutas:**\n* **Pendientes:** Ítem **Pendientes de Enfermería**.\n* **Evaluaciones:** Ítem **Evaluaciones / Escalas**.\n\n**Gestión de Pendientes (Otros):**\n* **Añadir:** Botón Añadir para crear un nuevo pendiente.\n* Para corregir un pendiente ya liberado, se debe **inactivar** y justificar la acción.\n        \n**Gestión de Evaluaciones/Escalas:**\n* Clic **Añadir** > Selecciona la evaluación que desees.\n* Completa, **Guarda y Libera**."
    },
    
    # === PERFIL MÉDICO / OTROS (Clave: nota clinica) ===
    "nota clinica": {
        "contenido": "### 📝 Notas Clínicas (Evoluciones)\n\n**Ruta:** Ítem **Nota Clínica**.\n\n**Pasos para Evolucionar:**\n1. Clic en **Añadir**.\n2. Elige **Tipo de nota clínica** (Tu especialidad) para usar plantillas.\n3. Completa los datos y **Liberar** para finalizar.\n\n**Tips:**\n* **Duplicar:** Clic derecho sobre nota previa > Duplicar nota clínica.\n* **Corregir:** Selecciona la nota > Clic sobre **Inactivar** y justifica el motivo."
    },
    "antecedentes_multi": {
        "contenido": "### 📜 Cargar/Ver Antecedentes del Paciente\n\n**Ruta:** Ítem **Antecedentes de Salud**.\n\n**Visualizar:** Haz clic en la solapa deseada (Alergias, Hábitos, Patológicas, etc.) para ver la información cargada.\n\n**Cargar:**\n1. Elige la solapa.\n2. Haz clic en **Añadir**.\n3. Completa el registro, **Guarda y Libera**.\n* Si marcas 'exhibir en alertas', aparecerá en el pop-up de seguridad al ingresar a la HCE."
    },
    "informe final": {
        "contenido": "### 🏁 Informe Final / Epicrisis\n\n**Ruta:** Función **Central de informes** (desde el menú principal).\n\n**Pasos para PDF:**\n1. El estatus del informe debe ser **'realizado'**.\n2. Clic derecho > **Ejecutar** > **Incluir interpretación PDF**.\n3. Asigna el médico responsable y OK.\n\n**Epicrisis/Resumen HC (Médico):** Utiliza el tipo de nota 'Resumen de HC' en Notas Clínicas."
    },
    "ged": {
        "contenido": "### 📂 Cargar Informe Inicial (GED)\n\n**Ruta:** Ítem **Gestión de Documentos**.\n\n**Pasos para Cargar:**\n1. Botón **Añadir**.\n2. Sube el archivo.\n3. **Clasifica** el archivo (selecciona 'informe inicial' en el tipo de archivo).\n4. **Liberar** para que sea visible."
    },
}


# --- 4. MOTOR DE BÚSQUEDA ---
# Esta función solo se usa si el usuario decide "dejar un mensaje" (modo libre)
def buscar_solucion(consulta, rol):
    q = consulta.lower()
    
    # Mapeo de búsqueda libre a claves de respuesta
    if any(x in q for x in ["contraseña", "usuario", "no veo paciente", "perfil"]): return base_de_conocimiento["login"]["contenido"]
    if any(x in q for x in ["pase de guardia", "resumen", "cama", "sector"]): return base_de_conocimiento["navegacion"]["contenido"]
    if any(x in q for x in ["sidca", "historia vieja", "anterior", "ces"]): return base_de_conocimiento["sidca"]["contenido"]

    # Enfermería
    if rol == "Enfermería":
        if any(x in q for x in ["signos", "vitales", "presion", "temperatura", "apap", "respiratoria"]): return base_de_conocimiento["signos vitales"]["contenido"]
        if any(x in q for x in ["balance", "hidrico", "ingreso", "egreso", "liquido"]): return base_de_conocimiento["balance hidrico"]["contenido"]
        if any(x in q for x in ["adep", "administrar", "medicacion", "droga", "glucemia", "revertir"]): return base_de_conocimiento["adep"]["contenido"]
        if any(x in q for x in ["dispositivo", "sonda", "via", "cateter", "equipo", "rotar"]): return base_de_conocimiento["dispositivos"]["contenido"]
        if any(x in q for x in ["pendiente", "tarea", "evaluacion", "escala", "score", "otros temas"]): return base_de_conocimiento["pendientes_eval"]["contenido"]
    
    # Médico / Otros Profesionales
    if rol in ["Médico", "Otros profesionales"]:
        if any(x in q for x in ["evolucionar", "nota", "escribir", "duplicar", "plantilla"]): return base_de_conocimiento["nota clinica"]["contenido"]
        if any(x in q for x in ["antecedentes", "cargar antecedentes"]): return base_de_conocimiento["antecedentes_multi"]["contenido"]
        if any(x in q for x in ["informe final", "epicrisis", "cargar informe"]): return base_de_conocimiento["informe final"]["contenido"]
        if any(x in q for x in ["cargar informe inicial", "ged", "documento"]): return base_de_conocimiento["ged"]["contenido"]

    # Default si no encuentra en modo libre
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
    st.session_state.response_key = None # Contiene la clave de la respuesta si se seleccionó un tag
if "conversation_step" not in st.session_state:
    st.session_state.conversation_step = "onboarding" # onboarding, tags, free_input, viewing_response, free_input_after_msg
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None # Guarda la última consulta para el log

# --- LÓGICA DE BARRA LATERAL (SETTINGS Y ACCIONES) ---
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

# 1. ONBOARDING
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

# --- 2. MOSTRAR HISTORIAL ---
if st.session_state.rol_usuario is not None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 3. FLUJO GUIADO POR TAGS (Enfermería, Médico, Otros) ---
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
    
    # 2. Renderiza la respuesta del bot
    with st.chat_message("assistant"):
        with st.spinner("Flenisito está buscando la solución..."):
            respuesta_core = base_de_conocimiento.get(key, "⚠️ No se encontró la ruta para ese tema. Por favor, intenta de nuevo.")
            st.markdown(respuesta_core)
            
            # 3. Pie de página y Navegación
            render_footer() # Llama a la función que renderiza el pie y el botón de descarga
            show_navigation_buttons(st.session_state.rol_usuario)

            # 4. Log y Mensajes de Sesión
            if prompt_from_tag:
                log_interaction(st.session_state.rol_usuario, prompt_from_tag, respuesta_core)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_core})
                st.session_state.response_key = None # Finaliza el procesamiento de la respuesta

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

        # 2. RESPUESTA DEL BOT (Busca en la base de conocimiento)
        with st.chat_message("assistant"):
            with st.spinner("Flenisito está buscando la solución..."):
                
                respuesta_core = buscar_solucion(prompt, st.session_state.rol_usuario)
                st.markdown(respuesta_core)
                
                # 3. Pie de página y Navegación
                render_footer() # Llama a la función que renderiza el pie y el botón de descarga
                show_navigation_buttons(st.session_state.rol_usuario)

                # 4. Log y Mensajes de Sesión
                log_interaction(st.session_state.rol_usuario, prompt, respuesta_core)
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
