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

# Definición de Tags de Enfermería (Se agrupan por destino de respuesta)
ENFERMERIA_TAGS = {
    "Glucemia (Cargar/Ver)": {"color": "#FFC0CB", "query": "glucemia", "response_key": "adep"},
    "Signos Vitales (Cargar/Ver)": {"color": "#ADD8E6", "query": "signos vitales", "response_key": "signos vitales"},
    "ADEP (Medicamentos y Dolor)": {"color": "#90EE90", "query": "administrar medicación si dolor", "response_key": "adep"},
    "Balance Hídrico (Turno/Día)": {"color": "#87CEFA", "query": "balance por turno", "response_key": "balance hidrico"},
    "Dispositivos (Catéter, Retiro)": {"color": "#F08080", "query": "agregar un nuevo catéter", "response_key": "dispositivos"},
    "Evaluaciones / Escalas": {"color": "#FFA07A", "query": "cargar escala de dolor", "response_key": "pendientes_eval"},
    "Pendientes de Enfermería": {"color": "#DDA0DD", "query": "agregar pendiente", "response_key": "pendientes_eval"},
    "Pase de Guardia / Resumen": {"color": "#FAFAD2", "query": "pase de guardia", "response_key": "navegacion"},
    "Login / Contraseña": {"color": "#B0C4DE", "query": "contraseña y usuario no coinciden", "response_key": "login"},
    "Consulta Histórica (SIDCA)": {"color": "#AFEEEE", "query": "consultar historia vieja", "response_key": "sidca"},
}

# Estilos CSS
st.markdown("""
    <style>
    .stChatMessage { border-radius: 10px; }
    .stButton button { width: 100%; border-radius: 5px; }
    h1 { color: #005490; }
    h3 { color: #005490; }
    
    /* Clase para reducir el tamaño de letra del pie de página */
    .footer-content {
        font-size: 0.9em; /* 90% del tamaño normal */
        opacity: 0.9;
    }
    /* Estilo para destacar el botón de descarga del manual */
    .stDownloadButton button {
        border: 1px solid #005490;
        color: #005490;
        background-color: #f0f8ff;
        margin-bottom: 10px;
    }
    .stDownloadButton button:hover {
        background-color: #005490;
        color: white;
    }
    
    /* Estilos para los botones de tags (colores pastel) */
    div[data-testid*="column"] > button {
        margin-bottom: 8px;
        color: #333333 !important; /* Texto oscuro para contraste */
        font-weight: bold;
        border: 1px solid #ddd;
    }
    
    /* Clases para aplicar los colores pastel de los tags */
    .tag-pink button { background-color: #FFC0CB; }
    .tag-lightblue button { background-color: #ADD8E6; }
    .tag-lightgreen button { background-color: #90EE90; }
    .tag-skyblue button { background-color: #87CEFA; }
    .tag-lightcoral button { background-color: #F08080; }
    .tag-lightsalmon button { background-color: #FFA07A; }
    .tag-thistle button { background-color: #DDA0DD; }
    .tag-lightyellow button { background-color: #FAFAD2; }
    .tag-slategray button { background-color: #B0C4DE; }
    .tag-turquoise button { background-color: #AFEEEE; }
    
    /* Estilos para los botones de navegación (Volver / Dejar mensaje) */
    .nav-button-container button {
        background-color: #f0f2f6;
        color: #005490 !important;
        border: 1px solid #005490;
        font-weight: 500;
        margin-top: 15px;
    }
    .nav-button-container button:hover {
        background-color: #005490;
        color: white !important;
    }

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

# Función para mostrar los botones de tags de Enfermería
def show_enfermeria_tags():
    st.markdown("### 🔍 Selecciona un Tema de Soporte de Enfermería:")
    
    tag_colors = {
        "Glucemia (Cargar/Ver)": "tag-pink",
        "Signos Vitales (Cargar/Ver)": "tag-lightblue",
        "ADEP (Medicamentos y Dolor)": "tag-lightgreen",
        "Balance Hídrico (Turno/Día)": "tag-skyblue",
        "Dispositivos (Catéter, Retiro)": "tag-lightcoral",
        "Evaluaciones / Escalas": "tag-lightsalmon",
        "Pendientes de Enfermería": "tag-thistle",
        "Pase de Guardia / Resumen": "tag-lightyellow",
        "Login / Contraseña": "tag-slategray",
        "Consulta Histórica (SIDCA)": "tag-turquoise",
    }
    
    # Crea una cuadrícula de 2 columnas para los botones
    cols = st.columns(2)
    
    for i, (label, data) in enumerate(ENFERMERIA_TAGS.items()):
        
        button_key = f"tag_enfermeria_{label.replace(' ', '_').replace('/', '_')}"
        
        # Uso de HTML para envolver el botón y aplicar el color pastel
        with cols[i % 2]:
            st.markdown(
                f'<div class="{tag_colors[label]}">', 
                unsafe_allow_html=True
            )
            # El botón de Streamlit se renderiza dentro del div coloreado
            if st.button(label, key=button_key, use_container_width=True):
                 # Al hacer clic, se establece la clave de respuesta y se rerenderiza
                 st.session_state.response_key = data['response_key']
                 st.session_state.last_prompt = data['query'] # Guarda el prompt para el log
                 st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# Función para mostrar los botones de navegación al final de la respuesta
def show_navigation_buttons(rol):
    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    
    # Botón 1: Volver un paso atrás (a la nube de tags o a la entrada libre)
    col_back, col_msg = st.columns(2)
    
    if rol == "Enfermería":
        back_label = "💉 Volver a Opciones de Enfermería"
        with col_back:
            if st.button(back_label, key="nav_back_enfermeria", use_container_width=True):
                st.session_state.conversation_step = "tags"
                st.session_state.response_key = None
                st.session_state.last_prompt = None
                st.rerun()
    else: # Perfiles Médico y Otros Profesionales (Vuelven al input de texto)
        back_label = "⬅️ Volver a Escribir una Consulta"
        with col_back:
            if st.button(back_label, key="nav_back_free", use_container_width=True):
                st.session_state.conversation_step = "free_input"
                st.session_state.response_key = None
                st.session_state.last_prompt = None
                st.rerun()

    # Botón 2: Dejar mensaje (Cambia al modo de input libre y notifica)
    with col_msg:
        if st.button("💬 No encontré respuesta (Dejar mensaje)", key="nav_leave_msg", use_container_width=True):
            st.session_state.conversation_step = "free_input"
            st.session_state.response_key = None
            st.session_state.last_prompt = None
            st.session_state.messages.append({"role": "assistant", "content": "Entendido. Por favor, describe tu problema con más detalle para que podamos ayudarte a encontrar la respuesta o derivar tu consulta al equipo de soporte."})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. BASE DE CONOCIMIENTO (Se mantiene igual, limpia de citas) ---
# NOTE: Se ha reagrupado "Pendientes" y "Evaluaciones" bajo "pendientes_eval"
# y "Evaluaciones Multi" para el resto de profesionales.
base_de_conocimiento = {
    # === TEMAS GENERALES ===
    "login": {
        "contenido": """
### 🔐 Acceso y Login

**Rutas:**
* URL: https://tasy.fleni.org.ar/#/login

**⚠️ Solución a Errores Frecuentes (Contraseña / Usuario):**
* **"No veo mis pacientes":** Revisa la esquina superior derecha.
    1. **Establecimiento:** ¿Dice Belgrano o Escobar?
    2. **Perfil:** ¿Es Hospitalización Multi o Enfermería?
    3. **Sector:** Es obligatorio seleccionar el sector en el filtro.
* **Cerrar Sesión:** Haz clic siempre en "Salir" (Logout).
        """
    },
    "navegacion": {
        "contenido": """
### 🧭 Navegación y Búsqueda

**Rutas (Pase de Guardia):**
* **Ver Camas:** Función "Perspectiva Clínica" > Elegir sector desde el filtro.
* **Resumen Electrónico:** Es la pantalla principal ideal para el pase de guardia, agrupando toda la información del paciente.

**Tips de Uso:**
* **Entrar a HCE:** Doble clic sobre el nombre del paciente.
* **Alertas:** Al entrar verás pop-ups de seguridad (Alergias/Aislamiento). Ciérralos con la X.
        """
    },
    "sidca": {
        "contenido": """
### 🕰️ Consulta Histórica (SIDCA)

**Ruta:**
* Desde cualquier parte de la Historia Clínica en Tasy.

**Pasos:**
1. Haz **clic derecho** en cualquier espacio en blanco de la pantalla.
2. Selecciona **CES - Consulta Electrónica de Salud**.
3. Se abrirá la ventana de SIDCA para ver los registros históricos cargados de ese paciente.
        """
    },

    # === PERFIL ENFERMERÍA ===
    "signos vitales": {
        "contenido": """
### 🩺 Signos Vitales y APAP (Cargar/Ver)

**Ruta:**
* Solapa **Signos Vitales** > Botón **Añadir**.

**Pasos Clave:**
1. Completa los campos y verifica la hora real.
2. **IMPORTANTE:** Marca la casilla **APAP** para que el dato viaje a la grilla general.
3. **Liberar** para finalizar.

**⚠️ Solución a Errores:**
* **Guardar vs Liberar:** *Guardar* es borrador (no visible). *Liberar* es publicar (visible para todos).
* **Corregir:** Si liberaste mal, selecciona el registro > **Inactivar** > Justificar motivo.
        """
    },
    "balance hidrico": {
        "contenido": """
### 💧 Balance Hídrico (Por Turno / Día)

**Ruta:**
* Solapa de **Ingresos y egresos**.

**Pasos para Cargar:**
1. Clic en **Añadir**.
2. Lado Izquierdo: Elige el Grupo y Tipo de líquido.
3. Clic en la **Flecha Derecha (➡️)** para pasarlo al panel de carga.
4. Se abre una ventana: pon el volumen y confirma con **Finalizar**.

**Visualización:**
* Ve a la solapa "**Análisis de balance**" para ver los totales por turno o por el día (puedes usar el filtro para cambiar la visualización).
        """
    },
    "adep": {
        "contenido": """
### 💊 ADEP (Glucemia y Medicación)

**Rutas:**
* Ítem **ADEP** en el árbol lateral para Medicación.
* Ítem **Exámenes y procedimientos** para Protocolo de Glucemia.

**Pasos (Medicamentos/Dolor):**
1. Busca el horario pendiente (lado derecho).
2. **Clic derecho** sobre el horario > **Administrar / revertir evento**.
3. **Nota:** Si es medicación condicional (ej. dolor), revisa la prescripción médica.

**Pasos (Glucemia - Cargar/Ver):**
1. En "Exámenes y procedimientos" das clic derecho e inicias el registro del valor de glucemia.
2. Los valores de glucemia cargados en ADEP impactan en APAP.
        """
    },
    "dispositivos": {
        "contenido": """
### 💉 Dispositivos (Agregar y Retirar Catéteres/Vías)

**Ruta:**
* Ítem **Dispositivos/Equipos**.

**Pasos (Agregar/Nuevo):**
* Ve a "Gráfico de dispositivos" > Nuevo dispositivo > Elige tipo y fecha de retiro/rotación.

**Pasos (Retirar):**
* Clic en "Acciones de dispositivo" > Selecciona el dispositivo > Justifica motivo y Ok.
* **Rotar:** Usa la acción **Sustituir**.
        """
    },
    "pendientes_eval": {
        "contenido": """
### 📋 Pendientes de Enfermería y Evaluaciones/Escalas

**Ruta:**
* Ítem **Pendientes de Enfermería** para tareas.
* Ítem **Evaluaciones / Escalas** para escalas.

**Gestión de Pendientes:**
* **Añadir:** Botón Añadir para crear recordatorio.
* Si ya se liberó, usa **Inactivar** justificando la acción.
        
**Gestión de Evaluaciones/Escalas (ej. Dolor):**
* Clic **Añadir** > Selecciona la evaluación deseada (ej. escala de dolor).
* Completa, **Guarda y Libera**.
        """
    },
    
    # === PERFIL MÉDICO / MULTI (Mantenemos por consistencia, no se usan en este flujo) ===
    "agenda": {"contenido": "La gestión de agenda requiere ingresar a Agenda de Servicio en el menú principal. Recuerda limpiar los filtros si vas a hacer una nueva búsqueda."},
    "nota clinica": {"contenido": "Las Notas Clínicas (Evoluciones) se crean haciendo clic en Añadir, seleccionando el tipo de nota (plantilla) y luego Liberar."},
    "informe final": {"contenido": "Para generar el Informe Final, usa la función Central de informes. El estatus debe estar como 'realizado' para ejecutar la inclusión del PDF."},
    "cpoe": {"contenido": "Las recomendaciones se indican en CPOE. Para pedidos y justificativas, usa el ítem Justificaciones/Solicitudes haciendo clic en Añadir."},
    "ged": {"contenido": "Gestión de Documentos (GED) permite visualizar archivos de admisión (Anexos) y cargar documentos propios. Usa Añadir y clasifica el archivo."},
    "evaluaciones_multi": {"contenido": "Las Evaluaciones y Escalas se encuentran en el ítem 'Evaluaciones'. Puedes añadir, completar, guardar y liberar el registro."},
}


# --- 4. MOTOR DE BÚSQUEDA ---
# Esta función solo se usa si el usuario decide "dejar un mensaje" (modo libre)
def buscar_solucion(consulta, rol):
    q = consulta.lower()
    
    # Búsqueda General
    if any(x in q for x in ["login", "ingresar", "usuario", "contraseña", "no veo paciente", "perfil"]): return base_de_conocimiento["login"]["contenido"]
    if any(x in q for x in ["buscar paciente", "sector", "cama", "alerta", "resumen", "pase de guardia"]): return base_de_conocimiento["navegacion"]["contenido"]
    if any(x in q for x in ["sidca", "historia vieja", "anterior", "ces", "consulta electronica"]): return base_de_conocimiento["sidca"]["contenido"]

    # Enfermería (Usa las mismas claves que los tags)
    if rol == "Enfermería":
        if any(x in q for x in ["signos", "vitales", "presion", "temperatura", "apap", "respiratoria"]): return base_de_conocimiento["signos vitales"]["contenido"]
        if any(x in q for x in ["balance", "hidrico", "ingreso", "egreso", "liquido"]): return base_de_conocimiento["balance hidrico"]["contenido"]
        if any(x in q for x in ["adep", "administrar", "medicacion", "droga", "glucemia", "revertir"]): return base_de_conocimiento["adep"]["contenido"]
        if any(x in q for x in ["dispositivo", "sonda", "via", "cateter", "equipo", "rotar"]): return base_de_conocimiento["dispositivos"]["contenido"]
        if any(x in q for x in ["pendiente", "tarea", "evaluacion", "escala", "score", "imagen"]): return base_de_conocimiento["pendientes_eval"]["contenido"]
    
    # Médico / Otros Profesionales
    if rol in ["Médico", "Otros profesionales"]:
        if any(x in q for x in ["agenda", "turno", "citado", "filtro"]): return base_de_conocimiento["agenda"]["contenido"]
        if any(x in q for x in ["nota", "evolucion", "escribir", "duplicar", "plantilla"]): return base_de_conocimiento["nota clinica"]["contenido"]
        if any(x in q for x in ["informe", "final", "alta", "epicrisis", "pdf", "mail"]): return base_de_conocimiento["informe final"]["contenido"]
        if any(x in q for x in ["cpoe", "indicacion", "prescripcion", "gases", "recomendacion", "justificacion", "pedido", "solicitud", "orden"]): return base_de_conocimiento["cpoe"]["contenido"]
        if any(x in q for x in ["ged", "archivo", "adjunto", "documento"]): return base_de_conocimiento["ged"]["contenido"]
        if any(x in q for x in ["evaluacion", "escala", "score", "imagen", "adjuntar"]): return base_de_conocimiento["evaluaciones_multi"]["contenido"]

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
    st.session_state.conversation_step = "onboarding" # onboarding, tags, free_input, viewing_response
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
            # Limpiar otros estados
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
    # Mostramos la imagen solo si existe
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
            st.session_state.messages.append({"role": "assistant", "content": "Hola Doctor/a. Estoy listo para guiarte. Pregúntame sobre **Agenda, Notas, Informe Final y CPOE**."})
            st.session_state.conversation_step = "free_input"
            st.rerun()

    with col3:
        if st.button("👥 **Otros profesionales**", key="btn_otros"):
            st.session_state.rol_usuario = "Otros profesionales"
            st.session_state.manual_file = MANUAL_OTROS
            st.session_state.manual_label = "Manual de Otros Profesionales Completo"
            st.session_state.messages.append({"role": "assistant", "content": "¡Bienvenido/a! Te asisto con **Agenda, Notas Clínicas, GED y Evaluaciones**. Por favor, ingresa tu consulta:"})
            st.session_state.conversation_step = "free_input"
            st.rerun()

# --- 2. MOSTRAR HISTORIAL ---
if st.session_state.rol_usuario is not None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 3. FLUJO DE ENFERMERÍA: TAGS Y RESPUESTAS ESTRUCTURADAS ---
if st.session_state.rol_usuario == "Enfermería":
    
    # A. MOSTRAR TAGS
    if st.session_state.conversation_step == "tags":
        show_enfermeria_tags()
        # Se necesita un input de texto para el caso "Otros" o si el usuario quiere escribir
        st.markdown("---")
        st.session_state.conversation_step = "free_input" # Se mueve a free_input si escribe
        prompt = st.chat_input("O escribe directamente aquí 'Otros' o tu consulta...")
        st.session_state.conversation_step = "tags" # Se mantiene en tags hasta que haya un prompt
        
        if prompt:
            st.session_state.conversation_step = "free_input" # Se establece para procesar la consulta libre
            st.rerun()

    # B. MOSTRAR RESPUESTA ESTRUCTURADA POR TAG
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
                
                # 3. Pie de página (Descarga y Navegación)
                st.markdown("---")
                
                # Botón de descarga (Manual de Enfermería)
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

                # Botones de navegación (Volver a tags o dejar mensaje)
                show_navigation_buttons(st.session_state.rol_usuario)

                # 4. Log y Mensajes de Sesión
                if prompt_from_tag:
                    log_interaction(st.session_state.rol_usuario, prompt_from_tag, respuesta_core)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_core})
                    st.session_state.response_key = None # Finaliza el procesamiento de la respuesta

# --- 4. FLUJO DE MÉDICO/OTROS Y MODO LIBRE (FREE INPUT) ---
elif st.session_state.conversation_step == "free_input":
    
    prompt = st.chat_input("Escribe tu consulta aquí...")

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
                
                # 3. Pie de página (Descarga y Navegación)
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

                # Botones de navegación (Volver a input o dejar mensaje)
                show_navigation_buttons(st.session_state.rol_usuario)

                # 4. Log y Mensajes de Sesión
                log_interaction(st.session_state.rol_usuario, prompt, respuesta_core)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_core})
                st.session_state.conversation_step = "viewing_response" # Cambia el estado para que se rerendericen los botones de navegación
                st.rerun()

# --- 5. VISUALIZACIÓN DE RESPUESTA LIBRE (Para que los botones de navegación aparezcan) ---
elif st.session_state.conversation_step == "viewing_response":
    # El contenido ya se renderizó. Solo mostramos los botones de navegación
    show_navigation_buttons(st.session_state.rol_usuario)
