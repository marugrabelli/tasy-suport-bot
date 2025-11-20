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

# Definición de Tags de Enfermería
ENFERMERIA_TAGS = {
    "Glucemia": {"color": "#63A4FF", "query": "cargar glucemia"},
    "Signos Vitales": {"color": "#00CC66", "query": "cargar signos vitales"},
    "ADEP / Medicación": {"color": "#FF6347", "query": "administrar medicación si dolor"},
    "Balance Hídrico": {"color": "#4682B4", "query": "balance por turno"},
    "Dispositivos (Catéter)": {"color": "#FFD700", "query": "agregar un nuevo catéter"},
    "Ver Pacientes / Login": {"color": "#8A2BE2", "query": "contraseña y usuario no coinciden"},
    "Pase de Guardia": {"color": "#FFA07A", "query": "pase de guardia"},
    "Evaluaciones / Escalas": {"color": "#20B2AA", "query": "cargar escala de dolor"},
    "Pendientes": {"color": "#FF69B4", "query": "agregar pendiente"},
    "Consulta Histórica (SIDCA)": {"color": "#40E0D0", "query": "consultar historia vieja"},
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
    
    /* Estilos para los botones de tags de Enfermería */
    div[data-testid*="column"] > button {
        margin-bottom: 5px;
        color: white !important;
        font-weight: bold;
    }
    
    /* Aplicar colores definidos en ENFERMERIA_TAGS */
    .tag-glucemia button { background-color: #63A4FF; border-color: #63A4FF; }
    .tag-signos button { background-color: #00CC66; border-color: #00CC66; }
    .tag-adep button { background-color: #FF6347; border-color: #FF6347; }
    .tag-balance button { background-color: #4682B4; border-color: #4682B4; }
    .tag-dispositivos button { background-color: #FFD700; border-color: #FFD700; color: #333 !important; }
    .tag-login button { background-color: #8A2BE2; border-color: #8A2BE2; }
    .tag-pase button { background-color: #FFA07A; border-color: #FFA07A; }
    .tag-evaluaciones button { background-color: #20B2AA; border-color: #20B2AA; }
    .tag-pendientes button { background-color: #FF69B4; border-color: #FF69B4; }
    .tag-sidca button { background-color: #40E0D0; border-color: #40E0D0; }

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
    st.markdown("### 🔍 Temas Frecuentes de Enfermería")
    
    # Mapeo de tags a clases CSS para colores
    tag_class_map = {
        "Glucemia": "tag-glucemia",
        "Signos Vitales": "tag-signos",
        "ADEP / Medicación": "tag-adep",
        "Balance Hídrico": "tag-balance",
        "Dispositivos (Catéter)": "tag-dispositivos",
        "Ver Pacientes / Login": "tag-login",
        "Pase de Guardia": "tag-pase",
        "Evaluaciones / Escalas": "tag-evaluaciones",
        "Pendientes": "tag-pendientes",
        "Consulta Histórica (SIDCA)": "tag-sidca",
    }
    
    # Crea una cuadrícula de 3 columnas para los botones
    cols = st.columns(3)
    
    for i, (label, data) in enumerate(ENFERMERIA_TAGS.items()):
        # Se envuelve el botón en un div con la clase CSS personalizada
        with cols[i % 3]:
            # El key es esencial para Streamlit
            button_key = f"tag_enfermeria_{label.replace(' ', '_')}"
            
            # Se usa st.markdown con HTML para aplicar la clase CSS al botón
            st.markdown(
                f"""
                <div class="{tag_class_map[label]}">
                    <button style="width: 100%; border-radius: 5px;" 
                            onclick="window.parent.postMessage({{eventType: 'streamlit:setComponentValue', data: {{type: 'text', value: '{data['query']}', key: '{button_key}'}}}}, '*')">
                        {label}
                    </button>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Nota: Dado que Streamlit no permite modificar el estilo del botón
            # directamente con `st.button` basado en el texto, se usa un truco
            # de HTML/JS para convertir el clic en una consulta.
            
            # Para simplificar la implementación y usar st.button:
            # Si prefieres la implementación más simple, usa solo `st.button`
            # y haz que el retorno sea el valor de la consulta.
            if st.button(label, key=button_key):
                 st.session_state.tags_clicked = data['query']
                 st.rerun()


# --- 3. BASE DE CONOCIMIENTO (Limpiada de cualquier cite start o formato de cita) ---
base_de_conocimiento = {
    # === TEMAS GENERALES ===
    "login": {
        "contenido": """
### 🔐 Acceso y Login

**Rutas:**
* URL: https://tasy.fleni.org.ar/#/login

**⚠️ Solución a Errores Frecuentes:**
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

**Rutas:**
* **Ver Camas:** Función "Perspectiva Clínica" > Elegir sector desde el filtro.
* **Entrar a HCE:** Doble clic sobre el nombre del paciente.

**Tips de Uso:**
* **Alertas:** Al entrar verás pop-ups de seguridad (Alergias/Aislamiento). Ciérralos con la X.
* **Resumen Electrónico:** Es la pantalla principal ideal para el pase de guardia.
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
3. Se abrirá la ventana de SIDCA para ver los registros cargados de ese paciente.
        """
    },

    # === PERFIL ENFERMERÍA ===
    "signos vitales": {
        "contenido": """
### 🩺 Signos Vitales y APAP (Enfermería)

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
### 💧 Balance Hídrico

**Ruta:**
* Solapa de **Ingresos y egresos**.

**Pasos para Cargar:**
1. Clic en **Añadir**.
2. Lado Izquierdo: Elige el Grupo y Tipo de líquido.
3. Clic en la **Flecha Derecha (➡️)** para pasarlo al panel de carga.
4. Se abre una ventana: pon el volumen y confirma con **Finalizar**.

**Visualización:**
* Ve a la solapa "**Análisis de balance**" para ver los totales por turno o día.
        """
    },
    "adep": {
        "contenido": """
### 💊 ADEP (Administración de Medicación y Glucemia)

**Ruta:**
* Ítem ADEP en el árbol lateral para Medicación.
* Ítem **Exámenes y procedimientos** para Protocolo de Glucemia.

**Pasos (Medicamentos):**
1. Busca el horario pendiente.
2. **Clic derecho** sobre el horario > **Administrar / revertir evento**.
3. Da OK.

**Pasos (Glucemia):**
1. En "Exámenes y procedimientos" das clic derecho e inicias el registro del valor de glucemia.
2. Los valores de glucemia cargados en ADEP impactan en APAP.
        """
    },
    "dispositivos": {
        "contenido": """
### 💉 Dispositivos (Sondas, Vías, Catéteres)

**Ruta:**
* Ítem **Dispositivos/Equipos**.

**Pasos:**
* **Nuevo:** Ve a "Gráfico de dispositivos" > Nuevo dispositivo.
* **Retirar:** Clic en "Acciones de dispositivo" > Selecciona el dispositivo > Justifica motivo y Ok.
* **Rotar:** Clic en "Acciones de dispositivo" > **Sustituir**.
        """
    },
    "pendientes": {
        "contenido": """
### 📋 Pendientes de Enfermería y Evaluaciones

**Ruta:**
* Ítem **Pendientes de Enfermería** para tareas.
* Ítem **Evaluaciones / Escalas** para escalas.

**Gestión de Pendientes:**
* **Añadir:** Botón Añadir para crear recordatorio.
* Si ya se liberó, usa **Inactivar** justificando la acción.
        
**Gestión de Evaluaciones:**
* Clic **Añadir** > Selecciona la evaluación deseada (ej. escala de dolor).
* Completa, **Guarda y Libera**.
        """
    },
    
    # === PERFIL MÉDICO / MULTI ===
    "agenda": {
        "contenido": """
### 📅 Gestión de Agenda (Turnos)

**Rutas:**
* **Agenda del día:** HCE > Consulta > Agenda de servicios.
* **Turnos libres:** Pantalla principal > Agenda de servicio.

**⚠️ Solución a Errores:**
* **"No veo nada":** Tienes que seleccionar previamente la agenda desde el filtro.
* **Estatus:** Luego de atender, cambia el estado de "esperando consulta" a **"ejecutada"**.
        """
    },
    "nota clinica": {
        "contenido": """
### 📝 Notas Clínicas (Evoluciones)

**Ruta:**
* Ítem **Nota Clínica**.

**Tips:**
* **Duplicar:** Clic derecho sobre nota previa > Duplicar nota clínica.
* **Alta Médica:** Usa el tipo de nota "**Resumen de HC**".
* **Finalizar:** Siempre **Liberar** para que sea visible.
        """
    },
    "informe final": {
        "contenido": """
### 🏁 Informe Final (Alta)

**Ruta:**
* Función **Central de informes**.

**Pasos para PDF:**
1. El estatus debe ser **"realizado"**.
2. Clic derecho sobre el informe > **Ejecutar** > **Incluir interpretación PDF**.
3. **Enviar por Email:** Cuando el estatus cambie a "**Interpretación liberada**", haz clic derecho > Enviar > email.
        """
    },
    "cpoe": {
        "contenido": """
### 💊 CPOE, Justificaciones y Pedidos

**Rutas:**
* **Ver Medicación/Indicaciones:** Árbol HCE > CPOE.
* **Justificaciones/Solicitudes:** Ítem para generar pedidos o documentos.

**Pasos (Indicaciones):**
* **Recomendaciones:** Despliega listado por servicio > Selecciona el check > Liberar y confirmar.
        """
    },
    "ged": {
        "contenido": """
### 📂 Gestión de Documentos (GED)

**Ruta:**
* Ítem **Gestión de Documentos**.

**Uso:**
* **Cargar:** Botón **Añadir**, y **clasifica** el archivo (ej. "informe inicial").
* **Visualizar:** Haciendo clic sobre Archivo.
        """
    },
    "evaluaciones_multi": { # Clave separada para evitar confusión con el tag de Enf.
        "contenido": """
### 📊 Evaluaciones y Escalas (Multi)

**Ruta:**
* Ítem **Evaluaciones**.

**Pasos:**
1. Clic **Añadir** > Selecciona la evaluación deseada.
2. Completa los campos.
3. **Guardar y Liberar**.
        """
    }
}

# --- 4. MOTOR DE BÚSQUEDA ---
def buscar_solucion(consulta, rol):
    q = consulta.lower()
    
    # Búsqueda General (Aplica a todos los roles)
    if any(x in q for x in ["login", "ingresar", "usuario", "contraseña", "no veo paciente", "perfil", "contraseña y usuario no coinciden"]): return base_de_conocimiento["login"]["contenido"]
    if any(x in q for x in ["buscar paciente", "sector", "cama", "alerta", "resumen", "pase de guardia"]): return base_de_conocimiento["navegacion"]["contenido"]
    if any(x in q for x in ["sidca", "historia vieja", "anterior", "ces", "consulta electronica", "consultar historia vieja"]): return base_de_conocimiento["sidca"]["contenido"]

    # Enfermería
    if rol == "Enfermería":
        # Signos Vitales y Glucemia (Ver/Cargar)
        if any(x in q for x in ["signos", "vitales", "presion", "temperatura", "apap", "respiratoria", "cargar signos vitales", "ver signos vitales"]): return base_de_conocimiento["signos vitales"]["contenido"]
        # Balance Hídrico (Por turno/día)
        if any(x in q for x in ["balance", "hidrico", "ingreso", "egreso", "liquido", "balance por turno", "balance por dia"]): return base_de_conocimiento["balance hidrico"]["contenido"]
        # ADEP y Medicación
        if any(x in q for x in ["adep", "administrar", "medicacion", "droga", "glucemia", "revertir", "adm medicación si dolor", "cargar glucemia", "ver glucemia"]): return base_de_conocimiento["adep"]["contenido"]
        # Dispositivos
        if any(x in q for x in ["dispositivo", "sonda", "via", "cateter", "equipo", "rotar", "agregar un nuevo catéter", "retirar catéter"]): return base_de_conocimiento["dispositivos"]["contenido"]
        # Pendientes / Evaluaciones (incluye escala de dolor)
        if any(x in q for x in ["pendiente", "tarea", "evaluacion", "escala", "score", "imagen", "cargar escala de dolor", "agregar pendiente"]): return base_de_conocimiento["pendientes"]["contenido"]
    
    # Médico / Otros Profesionales
    if rol in ["Médico", "Otros profesionales"]:
        if any(x in q for x in ["agenda", "turno", "citado", "filtro", "profesional", "consultar"]): return base_de_conocimiento["agenda"]["contenido"]
        if any(x in q for x in ["nota", "evolucion", "escribir", "duplicar", "plantilla", "resumen hc", "inactivar"]): return base_de_conocimiento["nota clinica"]["contenido"]
        if any(x in q for x in ["informe", "final", "alta", "epicrisis", "pdf", "mail", "central de informes"]): return base_de_conocimiento["informe final"]["contenido"]
        # CPOE / Justificaciones
        if any(x in q for x in ["cpoe", "indicacion", "prescripcion", "gases", "recomendacion", "justificacion", "pedido", "solicitud", "orden"]): return base_de_conocimiento["cpoe"]["contenido"]
        if any(x in q for x in ["ged", "archivo", "adjunto", "documento", "informe inicial", "anexos"]): return base_de_conocimiento["ged"]["contenido"]
        if any(x in q for x in ["evaluacion", "escala", "score", "imagen", "adjuntar"]): return base_de_conocimiento["evaluaciones_multi"]["contenido"]

    # Default
    msg = "⚠️ No encuentro una ruta exacta para esa consulta en los manuales.\n\n"
    if rol == "Enfermería":
        msg += "Temas disponibles: **Glucemia, Signos Vitales, ADEP, Balance Hídrico, Dispositivos, Pendientes**."
    else: # Médico o Otros Profesionales
        msg += "Temas disponibles: **Agenda, Notas Clínicas, Informe Final, CPOE/Pedidos, GED, Evaluaciones**."
    return msg

# --- 5. INTERFAZ DE USUARIO ---

st.title("🏥 Flenisito")
st.markdown("**Tu Asistente Virtual para Tasy en FLENI**")

if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tags_clicked" not in st.session_state:
    st.session_state.tags_clicked = None # Nuevo estado para manejar el clic del tag

# ONBOARDING (ESTRUCTURA DE TRES PERFILES)
if st.session_state.rol_usuario is None:
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
            st.session_state.messages.append({"role": "assistant", "content": "Hola colega. Soy Flenisito. Pregúntame sobre **Glucemia, Signos Vitales, ADEP o Dispositivos**."})
            st.rerun()
            
    with col2:
        if st.button("🩺 Soy **Médico/a**", key="btn_medico"):
            st.session_state.rol_usuario = "Médico"
            st.session_state.manual_file = MANUAL_MEDICOS
            st.session_state.manual_label = "Manual de Médicos Completo"
            st.session_state.messages.append({"role": "assistant", "content": "Hola Doctor/a. Estoy listo para guiarte en **Agenda, Notas, Informe Final y CPOE**."})
            st.rerun()

    with col3:
        if st.button("👥 **Otros profesionales**", key="btn_otros"):
            st.session_state.rol_usuario = "Otros profesionales"
            st.session_state.manual_file = MANUAL_OTROS
            st.session_state.manual_label = "Manual de Otros Profesionales Completo"
            st.session_state.messages.append({"role": "assistant", "content": "¡Bienvenido/a! Soy Flenisito. Te asisto con **Agenda, Notas Clínicas, GED y Evaluaciones**."})
            st.rerun()

# CHAT
else:
    with st.sidebar:
        st.success(f"Perfil activo: **{st.session_state.rol_usuario}**")
        
        # TIPS (CÓDIGO LIMPIO SIN CITES)
        st.markdown("---")
        st.markdown("### 💡 Tips Rápidos")
        st.caption("1. **Liberar** = Publicar. **Guardar** = Borrador.")
        st.caption("2. ¿No ves pacientes? Revisa **Sector** y **Establecimiento**.") 
        st.caption("3. **SIDCA:** Clic derecho > CES.")
        st.markdown("---")

        # ACCIONES
        if st.button("🔄 Cambiar de Perfil"):
            st.session_state.rol_usuario = None
            st.session_state.messages = []
            if "manual_file" in st.session_state:
                del st.session_state.manual_file
                del st.session_state.manual_label
            st.rerun()
        if st.button("🗑️ Borrar Chat"):
            st.session_state.messages = []
            st.rerun()
            
        # ADMIN LOGS
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

    # HISTORIAL
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Lógica para manejar el prompt
    prompt = st.chat_input("Escribe tu consulta aquí...")
    
    # 1. Chequea si se hizo clic en un tag de la nube
    if st.session_state.tags_clicked:
        prompt = st.session_state.tags_clicked
        st.session_state.tags_clicked = None # Limpia el estado
    
    # 2. Si es Enfermería y no hay prompt, muestra la nube de tags
    if st.session_state.rol_usuario == "Enfermería" and not prompt:
        show_enfermeria_tags()
        # No retorna nada, solo muestra los tags y espera input/click
        
    # 3. Procesa el prompt si existe (del chat_input o del tag_click)
    if prompt:
        # Añade el prompt (del tag o de la escritura) al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # RESPUESTA DEL BOT
        with st.chat_message("assistant"):
            with st.spinner("Flenisito está buscando la solución..."):
                
                # 1. Generar texto
                respuesta_core = buscar_solucion(prompt, st.session_state.rol_usuario)
                
                # Se renderiza la respuesta principal
                st.markdown(respuesta_core)
                
                # 2. SECCIÓN DEL PIE DE PÁGINA: BOTÓN DE DESCARGA Y MENSAJE
                st.markdown("---")
                
                # 2a. Botón de descarga (Muestra el botón si el archivo existe)
                if "manual_file" in st.session_state and os.path.exists(st.session_state.manual_file):
                    with open(st.session_state.manual_file, "rb") as f:
                        st.download_button(
                            label=f"📥 Descargar **{st.session_state.manual_label}**",
                            data=f,
                            file_name=os.path.basename(st.session_state.manual_file),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"descarga_{datetime.now().timestamp()}" 
                        )
                
                # 2b. Contenido del pie de página con tamaño de letra reducido
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

* 🖋️ **Firmas Digitales:** Envía tu firma en **formato JPG (fondo blanco)** a **soportesidca@fleni.org.ar**. Recuerda: **Sin firma, los médicos no pueden hacer recetas.**
* 📞 **Soporte Telefónico:** Llama al interno **5006**.
* 🎫 **Alta de Usuarios/VPN:** Deja un ticket en **solicitudes.fleni.org**.
""")
                    st.markdown('</div>', unsafe_allow_html=True)

                # 3. Log
                log_interaction(st.session_state.rol_usuario, prompt, respuesta_core)
                
                # Se guarda la respuesta en el historial
                st.session_state.messages.append({"role": "assistant", "content": respuesta_core})

