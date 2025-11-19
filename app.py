
import streamlit as st
import csv
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Soporte Tasy FLENI", page_icon="🏥", layout="wide")

# Estilos CSS para limpiar la interfaz
st.markdown("""
    <style>
    .stChatMessage { border-radius: 10px; }
    .stButton button { width: 100%; border-radius: 5px; }
    h1 { color: #005490; } /* Azul corporativo similar */
    </style>
    """, unsafe_allow_html=True)

# Archivo de logs
LOG_FILE = "registro_consultas_tasy.csv"

# --- 2. FUNCIONES DE BACKEND (LOGGING) ---
def log_interaction(rol, pregunta, respuesta):
    """Guarda la interacción en un CSV para análisis posterior del equipo."""
    file_exists = os.path.isfile(LOG_FILE)
    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Si es archivo nuevo, crear encabezados
            if not file_exists:
                writer.writerow(["Fecha", "Hora", "Rol", "Pregunta", "Respuesta_Bot"])
            
            now = datetime.now()
            writer.writerow([now.date(), now.strftime("%H:%M:%S"), rol, pregunta, respuesta])
    except Exception as e:
        st.error(f"Error al guardar log: {e}")

# --- 3. BASE DE CONOCIMIENTO (EL CEREBRO DEL BOT) ---
# Contiene la lógica extraída estrictamente de los manuales subidos.

base_de_conocimiento = {
    # === TEMAS GENERALES ===
    "login": {
        "contenido": """
        ### 🔐 Acceso y Login
        **Fuente:** Manuales Tasy
        
        [cite_start]**Ruta:** https://tasy.fleni.org.ar/#/login [cite: 2, 150]
        
        **Solución a "No veo pacientes/opciones":**
        [cite_start]Verifica en la esquina superior derecha[cite: 4, 152]:
        1.  [cite_start]**Establecimiento:** ¿Estás en Belgrano o Escobar? [cite: 5, 153]
        2.  [cite_start]**Perfil:** ¿Es el correcto (Hospitalización Multi vs Enfermería)? [cite: 5, 153]
        3.  **Sector:** Debes elegir el sector en el filtro para visualizar camas. [cite_start]Sin estos datos no podrás registrar ni ver pacientes[cite: 6, 154].
        """
    },
    "navegacion": {
        "contenido": """
        ### 🧭 Navegación y Pacientes
        
        **Búsqueda de Pacientes:**
        * [cite_start]**Por Sector:** "Perspectiva Clínica" > Elegir sector > Ver listado de camas[cite: 15, 21].
        * [cite_start]**Por Nombre/HC:** Usar el buscador por nombre o número de atención[cite: 24].
        * [cite_start]**Ingreso a HCE:** Doble clic sobre el nombre del paciente[cite: 25, 162].
        
        **Alertas:**
        Al ingresar, verás alertas de seguridad (Aislamiento, Alergias). [cite_start]Se pueden cerrar con la X[cite: 163, 164].
        """
    },
    "sidca": {
        "contenido": """
        ### 🕰️ Consulta Histórica (Sistema Anterior - SIDCA)
        
        Si necesitas ver registros antiguos que no están en Tasy:
        1.  En cualquier parte de la HCE (fondo blanco), haz **clic derecho**.
        2.  [cite_start]Selecciona **CES - Consulta Electrónica de Salud**[cite: 123, 325].
        3.  [cite_start]Esto te dirige a SIDCA para ver la historia clínica vieja[cite: 124, 326].
        """
    },

    # === PERFIL ENFERMERÍA ===
    "signos vitales": {
        "contenido": """
        ### 🩺 Signos Vitales y APAP (Enfermería)
        
        **1. Carga de Datos:**
        * [cite_start]Solapa **Signos Vitales** > Botón **Añadir**[cite: 185].
        * [cite_start]Completa los campos y la hora real del control[cite: 189].
        * [cite_start]**CRUCIAL:** Para que se vea en la grilla general, marca el check **APAP** al cargar[cite: 188].
        
        **2. Guardar vs. Liberar:**
        * **Guardar:** Es un borrador. Nadie más lo ve. [cite_start]Estado "no liberado"[cite: 192].
        * **Liberar:** Publica el dato. Visible para todos. [cite_start]No editable[cite: 194].
        
        **3. Corregir Error:**
        * [cite_start]Si liberaste con error: Selecciona registro > **Inactivar** > Justificar motivo[cite: 196].
        """
    },
    "balance hidrico": {
        "contenido": """
        ### 💧 Balance Hídrico
        
        [cite_start]**Visualización:** Solapa "Análisis de balance" (Izquierda: Total | Medio: Turno | Derecha: Detalle) [cite: 253-256].
        
        **Cómo Cargar (Ingresos/Egresos):**
        1.  [cite_start]Ve a la solapa **Ingresos y Egresos**[cite: 257].
        2.  [cite_start]Clic en **Añadir**[cite: 258].
        3.  Lado izquierdo: Selecciona Grupo y Tipo.
        4.  [cite_start]**PASO CLAVE:** Clic en la **Flecha Derecha** para pasarlo al lado derecho de la pantalla[cite: 261].
        5.  [cite_start]Se abre pop-up: detalla volumen y confirma con **Finalizar**[cite: 263, 264].
        """
    },
    "adep": {
        "contenido": """
        ### 💊 ADEP (Administración de Medicación)
        
        **Registrar Administración:**
        1.  [cite_start]Botón derecho sobre el horario pendiente > **Administrar / revertir evento**[cite: 219].
        2.  [cite_start]Opcional: Agregar comentario > Clic Ok[cite: 220, 221].
        
        **Medicación Suspendida:**
        * [cite_start]Usar el filtro y marcar el check "medicación suspendida" > Filtrar[cite: 229].
        
        **Glucemia (Protocolo):**
        * [cite_start]En "Exámenes y procedimientos" > Clic derecho > Registrar valor[cite: 238, 239].
        * El sistema sugiere corrección. [cite_start]Confirmar desde "control de glucemia"[cite: 240, 241].
        """
    },
    "dispositivos": {
        "contenido": """
        ### 💉 Dispositivos (Sondas, Vías)
        
        **Nuevo Dispositivo:**
        * [cite_start]Gráfico de dispositivos > Nuevo dispositivo > Elegir tipo y fecha prevista de retiro[cite: 271, 272].
        
        **Retirar o Rotar:**
        * [cite_start]Clic en **Acciones de dispositivo**[cite: 274].
        * [cite_start]Elegir "Retirar" (con justificación) o "Sustituir" (para rotación)[cite: 276, 277].
        """
    },

    # === PERFIL MÉDICO / MULTI ===
    "agenda": {
        "contenido": """
        ### 📅 Gestión de Agenda (Turnos)
        
        **Rutas:**
        * [cite_start]**Agenda del día:** HCE > Consulta > Agenda de servicios[cite: 11, 12].
        * [cite_start]**Turnos libres:** Pantalla principal > Agenda de servicio[cite: 30].
        
        **Cómo filtrar correctamente:**
        1.  [cite_start]**Por Especialidad:** Agenda de servicios > Consultar Datos > **Filtro avanzado** > Seleccionar agendas > Filtrar[cite: 32, 34].
        2.  [cite_start]**Por Profesional:** Usar la lupa en campo "Profesional ejecutor"[cite: 37].
        
        **⚠️ Solución a Errores:**
        * [cite_start]"No veo nada": Tienes que seleccionar previamente la agenda desde el filtro[cite: 13].
        * [cite_start]"Datos mezclados": Debes usar **Limpiar filtros** antes de una nueva búsqueda[cite: 35].
        """
    },
    "nota clinica": {
        "contenido": """
        ### 📝 Notas Clínicas (Evoluciones)
        
        **Crear Nota:**
        1.  [cite_start]Clic en **Añadir**[cite: 68].
        2.  Seleccionar **Tipo de nota clínica** (Tu especialidad).
        3.  [cite_start]Para el Alta: Usar tipo "Resumen de HC"[cite: 71].
        
        **Duplicar:**
        * [cite_start]Clic derecho sobre nota anterior > Duplicar[cite: 80].
        * [cite_start]**Ojo:** Si duplicas la nota de otro, borra su firma, ya que trae la del profesional original[cite: 81].
        
        **Importante:**
        * Siempre **Liberar** para finalizar. [cite_start]Si solo guardas, queda invisible para el resto[cite: 75, 76].
        """
    },
    "informe final": {
        "contenido": """
        ### 🏁 Informe Final (Alta)
        
        [cite_start]**Ruta:** Central de informes (Menu principal o llamada externa)[cite: 134, 136].
        
        **Pasos para PDF:**
        1.  [cite_start]El estatus debe ser **"Realizado"**[cite: 140].
        2.  [cite_start]Clic derecho > **Ejecutar** > **Incluir interpretación PDF**[cite: 141].
        3.  [cite_start]Seleccionar PDF, asignar médico y OK[cite: 142].
        
        **Enviar por Email:**
        * El estatus debe estar en "Interpretación liberada".
        * [cite_start]Clic derecho > Enviar > Email[cite: 143].
        """
    },
    "cpoe": {
        "contenido": """
        ### 💊 CPOE y Pedidos
        
        * [cite_start]**Ver Medicación:** Árbol HCE > CPOE[cite: 104].
        * [cite_start]**Dejar Recomendaciones:** Desplegar listado por servicio > Check en las deseadas > Liberar y confirmar[cite: 106, 107].
        * [cite_start]**Justificaciones/Pedidos:** Ítem "Justificaciones/Solicitudes" > Añadir > Elegir tipo > Guardar y Liberar [cite: 84-86].
        """
    }
}

# --- 4. MOTOR DE BÚSQUEDA INTELIGENTE ---
def buscar_solucion(consulta, rol):
    q = consulta.lower()
    
    # Mapeo de palabras clave a claves del diccionario
    # 1. Login y Accesos
    if any(x in q for x in ["login", "ingresar", "usuario", "contraseña", "no veo paciente", "perfil"]):
        return base_de_conocimiento["login"]["contenido"]
    
    # 2. Navegación / Pacientes
    if any(x in q for x in ["buscar paciente", "sector", "cama", "alerta", "resumen"]):
        return base_de_conocimiento["navegacion"]["contenido"]
        
    # 3. SIDCA / Historia Vieja
    if any(x in q for x in ["sidca", "historia vieja", "anterior", "ces", "consulta electronica"]):
        return base_de_conocimiento["sidca"]["contenido"]

    # --- TEMAS DE ENFERMERÍA ---
    if any(x in q for x in ["signos", "vitales", "presion", "temperatura", "apap"]):
        return base_de_conocimiento["signos vitales"]["contenido"]
        
    if any(x in q for x in ["balance", "hidrico", "ingreso", "egreso", "liquido"]):
        return base_de_conocimiento["balance hidrico"]["contenido"]
        
    if any(x in q for x in ["adep", "administrar", "medicacion", "droga", "glucemia", "revertir"]):
        return base_de_conocimiento["adep"]["contenido"]
        
    if any(x in q for x in ["dispositivo", "sonda", "via", "cateter"]):
        return base_de_conocimiento["dispositivos"]["contenido"]

    # --- TEMAS MULTI ---
    if any(x in q for x in ["agenda", "turno", "citado", "filtro"]):
        return base_de_conocimiento["agenda"]["contenido"]
        
    if any(x in q for x in ["nota", "evolucion", "escribir", "duplicar", "plantilla"]):
        return base_de_conocimiento["nota clinica"]["contenido"]
        
    if any(x in q for x in ["informe", "final", "alta", "epicrisis", "pdf", "mail"]):
        return base_de_conocimiento["informe final"]["contenido"]
        
    if any(x in q for x in ["cpoe", "indicacion", "pedido", "justificacion", "solicitud"]):
        return base_de_conocimiento["cpoe"]["contenido"]

    # Respuesta por defecto si no entiende
    msg = "⚠️ No encuentro una ruta exacta para esa consulta en los manuales.\n\n"
    if rol == "Enfermería":
        msg += "Temas disponibles para Enfermería: **Signos Vitales, Balance Hídrico, ADEP, Glucemia, Dispositivos**."
    else:
        msg += "Temas disponibles para Multi: **Agenda, Notas Clínicas, Informe Final, CPOE, Pedidos**."
    return msg

# --- 5. INTERFAZ DE USUARIO (FRONTEND) ---

st.title("🏥 Soporte Tasy FLENI")
st.markdown("**Asistente Virtual para Hospitalización Multi y Enfermería**")

# Inicializar estado de sesión
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- PANTALLA 1: SELECCIÓN DE ROL (ONBOARDING) ---
if st.session_state.rol_usuario is None:
    st.info("👋 ¡Hola! Para darte las rutas correctas del menú, por favor selecciona tu perfil:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💉 Soy Enfermería"):
            st.session_state.rol_usuario = "Enfermería"
            st.session_state.messages.append({"role": "assistant", "content": "Hola colega. Puedo ayudarte con **Signos Vitales, Balance, ADEP y Dispositivos**. ¿Qué necesitas?"})
            st.rerun()
            
    with col2:
        if st.button("🩺 Soy Médico / Multi"):
            st.session_state.rol_usuario = "Médico / Multi"
            st.session_state.messages.append({"role": "assistant", "content": "Hola Doctor/a o Licenciado/a. Estoy listo para guiarte en **Agenda, Notas Clínicas, Informe Final y CPOE**. ¿Cuál es tu consulta?"})
            st.rerun()

# --- PANTALLA 2: CHAT PRINCIPAL ---
else:
    # Sidebar con herramientas
    with st.sidebar:
        st.success(f"Perfil: **{st.session_state.rol_usuario}**")
        
        st.markdown("---")
        st.markdown("### 💡 Tips Rápidos")
        st.caption("1. **Liberar** es publicar. **Guardar** es borrador.")
        st.caption("2. Verifica siempre **Sector** y **Establecimiento**.")
        
        st.markdown("---")
        if st.button("🔄 Cambiar de Perfil"):
            st.session_state.rol_usuario = None
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🗑️ Borrar Chat"):
            st.session_state.messages = []
            # Reiniciamos con el saludo correspondiente
            saludo = "Hola colega." if st.session_state.rol_usuario == "Enfermería" else "Hola Doctor/a."
            st.session_state.messages.append({"role": "assistant", "content": f"{saludo} ¿En qué más puedo ayudarte?"})
            st.rerun()

    # Mostrar historial de chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Capturar input del usuario
    if prompt := st.chat_input("Escribe tu consulta aquí... (Ej: 'Cómo cargo un balance', 'Problema con agenda')"):
        
        # 1. Mostrar mensaje usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Procesar y buscar respuesta
        with st.chat_message("assistant"):
            with st.spinner("Buscando en manuales..."):
                
                respuesta = buscar_solucion(prompt, st.session_state.rol_usuario)
                st.markdown(respuesta)
                
                # 3. Guardar en Log (CSV)
                log_interaction(st.session_state.rol_usuario, prompt, respuesta)
        
        # 4. Guardar en historial
        st.session_state.messages.append({"role": "assistant", "content": respuesta})




