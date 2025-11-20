import streamlit as st
import csv
import os
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Flenisito - Soporte Tasy", page_icon="🏥", layout="wide")

# Archivos de Manuales (Verificación: Los nombres deben coincidir con GitHub)
LOG_FILE = "registro_consultas_flenisito.csv"
MANUAL_ENFERMERIA = "manual enfermeria (2).docx" 
MANUAL_MEDICOS = "Manual_Medicos.docx" # <-- Este es el nombre correcto
MANUAL_OTROS = "Manual Otros profesionales.docx" # Se mantiene el nombre del archivo en GitHub

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
        margin-bottom: 10px; /* Separación con el título de abajo */
    }
    .stDownloadButton button:hover {
        background-color: #005490;
        color: white;
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
        # st.error(f"Error al guardar log: {e}") 
        pass

# --- 3. BASE DE CONOCIMIENTO (Se mantiene igual, limpia de citas) ---
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
2. Lado Izquierdo: Elige el Grupo y Tipo de líquido, haciendo clic en la flecha para desplegar el listado.
3. Clic en la **Flecha Derecha (➡️)** para pasarlo al panel de carga.
4. Se abre una ventana: pon el volumen y confirma con **Finalizar**.

**Visualización:**
* Ve a la solapa "**Análisis de balance**" para ver los totales por turno.
        """
    },
    "adep": {
        "contenido": """
### 💊 ADEP (Administración de Medicación)

**Ruta:**
* Ítem ADEP en el árbol lateral.

**Pasos:**
1. Busca el horario pendiente (lado derecho).
2. **Clic derecho** sobre el horario > **Administrar / revertir evento**.
3. Da OK para confirmar el registro.

**Casos Especiales:**
* **Medicación Suspendida:** Usa el filtro y marca "medicación suspendida".
* **Glucemia (Protocolo):** En "Exámenes y procedimientos" das clic derecho e inicias el registro del valor. Los valores impactan en APAP.
        """
    },
    "dispositivos": {
        "contenido": """
### 💉 Dispositivos (Sondas, Vías, Catéteres)

**Ruta:**
* Ítem **Dispositivos/Equipos**.

**Pasos:**
* **Nuevo:** Ve a "Gráfico de dispositivos" > Nuevo dispositivo > Elige tipo, fecha de retiro y agrega detalles/observaciones.
* **Retirar:** Clic en "Acciones de dispositivo" > Selecciona el dispositivo > Justifica motivo y Ok.
* **Rotar:** Clic en "Acciones de dispositivo" > **Sustituir**.
        """
    },
    "pendientes": {
        "contenido": """
### 📋 Pendientes de Enfermería

**Ruta:**
* Ítem **Pendientes de Enfermería**.

**Gestión:**
* **Añadir:** Botón Añadir para crear recordatorio.
* **Borrar/Corregir:**
    * Si no está liberado, puedes **Eliminar pendiente**.
    * Si ya se liberó, usa **Inactivar** justificando la acción.
        """
    },

    # === PERFIL MÉDICO / MULTI ===
    "agenda": {
        "contenido": """
### 📅 Gestión de Agenda (Turnos)

**Rutas:**
* **Agenda del día:** HCE > Consulta > Agenda de servicios.
* **Turnos libres:** Pantalla principal > Agenda de servicio.

**Cómo Filtrar Correctamente:**
1. **Por Especialidad:** Agenda de servicio > Consultar Datos > Filtro avanzado > Seleccionar todas las agendas del servicio > Filtrar.
2. **Por Profesional:** Utiliza el segmento "profesional ejecutor" y la lupa.

**⚠️ Solución a Errores:**
* **"No veo nada":** Tienes que seleccionar previamente la agenda desde el filtro.
* **Estatus:** Luego de atender, cambia el estado de "esperando consulta" a **"ejecutada"**.
* **Nueva Búsqueda:** Obligatorio usar el botón **Limpiar filtros** antes de hacer una nueva búsqueda.
        """
    },
    "nota clinica": {
        "contenido": """
### 📝 Notas Clínicas (Evoluciones)

**Ruta:**
* Ítem **Nota Clínica**.

**Pasos:**
1. Clic en **Añadir**.
2. Elige **Tipo de nota clínica** (Tu especialidad) para usar plantillas.
3. Completa los datos y **Liberar** para finalizar.

**Tips:**
* **Alta Médica:** Usa el tipo de nota "**Resumen de HC**".
* **Duplicar:** Clic derecho sobre nota previa > Duplicar nota clínica. **Importante:** Si la nota no es tuya, borra la firma del profesional original.
* **Corregir:** Selecciona la nota > Clic sobre **Inactivar** y justifica el motivo.
        """
    },
    "informe final": {
        "contenido": """
### 🏁 Informe Final (Alta)

**Ruta:**
* Función **Central de informes** (desde la pantalla principal o desde la HCE usando la llamada externa).

**Pasos para PDF:**
1. **Importante:** El estatus debe ser **"realizado"**.
2. Clic derecho sobre el informe > **Ejecutar** > **Incluir interpretación PDF**.
3. Asigna el médico responsable y da OK.

**Enviar por Email:**
* Cuando el estatus cambie a "**Interpretación liberada**", haz clic derecho > Enviar > email.
* Si el paciente no tiene mail, puedes usar "email electivo" o avisar a secretaría.
        """
    },
    "cpoe": {
        "contenido": """
### 💊 CPOE, Justificaciones y Pedidos

**Rutas:**
* **Ver Medicación/Indicaciones:** Árbol HCE > CPOE.
* **Justificaciones/Solicitudes:** Ítem para generar pedidos o documentos (ej. pre-informes).

**Pasos (Indicaciones):**
* **Recomendaciones:** Despliega listado por servicio > Selecciona el check de las deseadas > Liberar y confirmar.
* **Nota:** Si no encuentras la recomendación, usa la **recomendación general** y detalla en el campo información adicional.

**Pasos (Justificaciones):**
* Clic en **Añadir** > Seleccionar tipo de justificativa > Completar, guardar y liberar.
* Para PDF: Selecciona el registro, haz clic en **reportes > visualizar**.
        """
    },
    "ged": {
        "contenido": """
### 📂 Gestión de Documentos (GED)

**Ruta:**
* Ítem **Gestión de Documentos**.

**Uso:**
* **Visualizar:** Haciendo clic sobre Archivo.
* **Contenido:** Contiene archivos cargados por administrativos (solapa Anexos) y profesionales (solapa Documentos).
* **Cargar:** Botón **Añadir**, y **clasifica** el archivo (ej. "informe inicial").
* **Buscar:** Utiliza el filtro con fechas y tipo de archivos.
        """
    },
    "evaluaciones": {
        "contenido": """
### 📊 Evaluaciones y Escalas

**Ruta:**
* Ítem **Evaluaciones**.

**Pasos:**
1. Clic **Añadir** > Selecciona la evaluación deseada.
2. Completa los campos.
3. **Guardar y Liberar**.

**Tips:**
* **Adjuntar Imagen/Anexo:** Guarda primero (sin liberar), ve a la solapa **Anexos**, agrega el archivo y luego **Libera**.
* **Duplicar:** Clic derecho sobre evaluación previa > Duplicar. Luego Guardar y Liberar.
        """
    }
}

# --- 4. MOTOR DE BÚSQUEDA (Se mantiene igual, la lógica es correcta) ---
def buscar_solucion(consulta, rol):
    q = consulta.lower()
    
    # Búsqueda General (Aplica a todos los roles)
    if any(x in q for x in ["login", "ingresar", "usuario", "contraseña", "no veo paciente", "perfil"]): return base_de_conocimiento["login"]["contenido"]
    if any(x in q for x in ["buscar paciente", "sector", "cama", "alerta", "resumen"]): return base_de_conocimiento["navegacion"]["contenido"]
    if any(x in q for x in ["sidca", "historia vieja", "anterior", "ces", "consulta electronica"]): return base_de_conocimiento["sidca"]["contenido"]

    # Enfermería
    if rol == "Enfermería":
        if any(x in q for x in ["signos", "vitales", "presion", "temperatura", "apap", "respiratoria"]): return base_de_conocimiento["signos vitales"]["contenido"]
        if any(x in q for x in ["balance", "hidrico", "ingreso", "egreso", "liquido"]): return base_de_conocimiento["balance hidrico"]["contenido"]
        if any(x in q for x in ["adep", "administrar", "medicacion", "droga", "glucemia", "revertir"]): return base_de_conocimiento["adep"]["contenido"]
        if any(x in q for x in ["dispositivo", "sonda", "via", "cateter", "equipo", "rotar"]): return base_de_conocimiento["dispositivos"]["contenido"]
        if any(x in q for x in ["pendiente", "tarea"]): return base_de_conocimiento["pendientes"]["contenido"]
    
    # Médico / Otros Profesionales
    if rol in ["Médico", "Otros profesionales"]:
        if any(x in q for x in ["agenda", "turno", "citado", "filtro", "profesional", "consultar"]): return base_de_conocimiento["agenda"]["contenido"]
        if any(x in q for x in ["nota", "evolucion", "escribir", "duplicar", "plantilla", "resumen hc", "inactivar"]): return base_de_conocimiento["nota clinica"]["contenido"]
        if any(x in q for x in ["informe", "final", "alta", "epicrisis", "pdf", "mail", "central de informes"]): return base_de_conocimiento["informe final"]["contenido"]
        # CPOE / Justificaciones
        if any(x in q for x in ["cpoe", "indicacion", "prescripcion", "gases", "recomendacion", "justificacion", "pedido", "solicitud", "orden"]): return base_de_conocimiento["cpoe"]["contenido"]
        if any(x in q for x in ["ged", "archivo", "adjunto", "documento", "informe inicial", "anexos"]): return base_de_conocimiento["ged"]["contenido"]
        if any(x in q for x in ["evaluacion", "escala", "score", "imagen", "adjuntar"]): return base_de_conocimiento["evaluaciones"]["contenido"]

    # Default
    msg = "⚠️ No encuentro una ruta exacta para esa consulta en los manuales.\n\n"
    if rol == "Enfermería":
        msg += "Temas disponibles: **Signos Vitales, Balance Hídrico, ADEP, Glucemia, Dispositivos, Pendientes**."
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
            # Asignación correcta
            st.session_state.manual_file = MANUAL_ENFERMERIA
            st.session_state.manual_label = "Manual de Enfermería Completo"
            st.session_state.messages.append({"role": "assistant", "content": "Hola colega. Soy Flenisito. Pregúntame sobre **Signos Vitales, Balance, ADEP o Dispositivos**."})
            st.rerun()
            
    with col2:
        if st.button("🩺 Soy **Médico/a**", key="btn_medico"):
            st.session_state.rol_usuario = "Médico"
            # Asignación correcta
            st.session_state.manual_file = MANUAL_MEDICOS
            st.session_state.manual_label = "Manual de Médicos Completo"
            st.session_state.messages.append({"role": "assistant", "content": "Hola Doctor/a. Estoy listo para guiarte en **Agenda, Notas, Informe Final y CPOE**."})
            st.rerun()

    with col3:
        if st.button("👥 **Otros profesionales**", key="btn_otros"):
            st.session_state.rol_usuario = "Otros profesionales"
            # Asignación correcta
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

    # INPUT
    if prompt := st.chat_input("Escribe tu consulta aquí..."):
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

