import streamlit as st
import csv
import os
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Flenisito - Soporte Tasy", page_icon="🏥", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .stChatMessage { border-radius: 10px; }
    .stButton button { width: 100%; border-radius: 5px; }
    h1 { color: #005490; }
    h3 { color: #005490; }
    /* Estilo para destacar el botón de descarga del manual */
    .stDownloadButton button {
        border: 1px solid #005490;
        color: #005490;
        background-color: #f0f8ff;
    }
    .stDownloadButton button:hover {
        background-color: #005490;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Archivos
LOG_FILE = "registro_consultas_flenisito.csv"
# Asegúrate de subir este archivo exacto a tu GitHub
MANUAL_ENFERMERIA = "manual enfermeria (2).docx" 

# --- MENSAJE DE PIE DE PÁGINA ---
MENSAJE_PIE = """
---
### 💡 Antes de llamar, ¡revisa estos puntos!

* **💻 Navegador Ideal:** Usa siempre **Google Chrome**.
* **🧹 Limpieza:** Si algo no carga, prueba a **limpiar la caché** (`Ctrl + H`).
* [cite_start]**👤 Perfil:** Verifica que tu **Log In** esté en el **establecimiento y perfil correcto** (Ej: Hospitalización Multi/Enfermería)[cite: 5, 153].
* **🔍 Zoom:** ¿Pantalla cortada? Ajusta el zoom: **`Ctrl + +`** (agrandar) o **`Ctrl + -`** (minimizar).

---
**¿Aún tienes dudas?**

* 🖋️ **Firmas Digitales:** Envía tu firma en **formato JPG (fondo blanco)** a **soportesidca@fleni.org.ar**. Recuerda: **Sin firma, los médicos no pueden hacer recetas.**
* 📞 **Soporte Telefónico:** Llama al interno **5006**.
* 🎫 **Alta de Usuarios/VPN:** Deja un ticket en **solicitudes.fleni.org**.
"""

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
        st.error(f"Error al guardar log: {e}")

# --- 3. BASE DE CONOCIMIENTO ---
base_de_conocimiento = {
    # === TEMAS GENERALES ===
    "login": {
        "contenido": f"""
### 🔐 Acceso y Login

**Rutas:**
* [cite_start]URL: https://tasy.fleni.org.ar/#/login [cite: 2, 150]

**⚠️ Solución a Errores Frecuentes:**
* [cite_start]**"No veo mis pacientes":** Revisa la esquina superior derecha[cite: 4, 152].
    1. [cite_start]**Establecimiento:** ¿Dice Belgrano o Escobar? [cite: 5, 153]
    2. [cite_start]**Perfil:** ¿Es Hospitalización Multi o Enfermería? [cite: 5, 153]
    3. [cite_start]**Sector:** Es obligatorio seleccionar el sector en el filtro[cite: 5, 153].
* [cite_start]**Cerrar Sesión:** Haz clic siempre en "Salir" (Logout)[cite: 8, 156].
        """
    },
    "navegacion": {
        "contenido": """
### 🧭 Navegación y Búsqueda

**Rutas:**
* [cite_start]**Ver Camas:** Función "Perspectiva Clínica" > Elegir sector[cite: 15, 16].
* [cite_start]**Entrar a HCE:** Doble clic sobre el nombre del paciente[cite: 25, 162].

**Tips de Uso:**
* [cite_start]**Alertas:** Al entrar verás pop-ups de seguridad (Alergias/Aislamiento)[cite: 163, 167, 168]. [cite_start]Ciérralos con la X[cite: 164].
* [cite_start]**Resumen Electrónico:** Es la pantalla principal ideal para el pase de guardia[cite: 179].
        """
    },
    "sidca": {
        "contenido": """
### 🕰️ Consulta Histórica (SIDCA)

**Ruta:**
* [cite_start]Desde cualquier parte de la Historia Clínica en Tasy[cite: 123, 325].

**Pasos:**
1. [cite_start]Haz **clic derecho** en cualquier espacio en blanco de la pantalla[cite: 123, 325].
2. [cite_start]Selecciona **CES - Consulta Electrónica de Salud**[cite: 123, 325].
3. [cite_start]Se abrirá la ventana de SIDCA para ver evoluciones viejas[cite: 124, 326].
        """
    },

    # === PERFIL ENFERMERÍA ===
    "signos vitales": {
        "contenido": """
### 🩺 Signos Vitales y APAP (Enfermería)

**Ruta:**
* [cite_start]Solapa **Signos Vitales** [cite: 183] > [cite_start]Botón **Añadir**[cite: 185].

**Pasos Clave:**
1. [cite_start]Completa los campos y verifica la hora real[cite: 189].
2. [cite_start]**IMPORTANTE:** Marca la casilla **APAP** para que el dato viaje a la grilla general[cite: 188, 195].

**⚠️ Solución a Errores:**
* **Guardar vs Liberar:**
    * [cite_start]*Guardar:* Es borrador (nadie más lo ve)[cite: 192]. [cite_start]Permite editar[cite: 193].
    * [cite_start]*Liberar:* Publicar (visible para todos)[cite: 194]. [cite_start]No permite editar, solo inactivar[cite: 194].
* [cite_start]**Corregir:** Si liberaste mal, selecciona el registro > **Inactivar** > Justificar motivo[cite: 196, 197].
        """
    },
    "balance hidrico": {
        "contenido": """
### 💧 Balance Hídrico

**Ruta:**
* [cite_start]Solapa de **Ingresos y egresos**[cite: 257].

**Pasos para Cargar:**
1. [cite_start]Clic en **Añadir**[cite: 258].
2. [cite_start]Lado Izquierdo: Elige el Grupo y Tipo de líquido[cite: 259].
3. [cite_start]**CRUCIAL:** Clic en la **Flecha Derecha (➡️)** para pasarlo al panel de carga[cite: 261].
4. [cite_start]Se abre una ventana: pon el volumen y confirma con **Finalizar**[cite: 263, 264].

**Visualización:**
* [cite_start]Ve a la solapa "**Análisis de balance**" para ver los totales por turno[cite: 253, 255].
        """
    },
    "adep": {
        "contenido": """
### 💊 ADEP (Administración de Medicación)

**Ruta:**
* [cite_start]Ítem ADEP en el árbol lateral[cite: 213].

**Pasos:**
1. [cite_start]Busca el horario pendiente (lado derecho)[cite: 213].
2. [cite_start]**Clic derecho** sobre el horario > **Administrar / revertir evento**[cite: 219].
3. [cite_start]Agrega comentario si hace falta y da OK[cite: 220, 221].

**Casos Especiales:**
* [cite_start]**Medicación Suspendida:** Usa el filtro arriba y marca "medicación suspendida", luego filtra[cite: 229].
* [cite_start]**Glucemia (Protocolo):** Se carga en "Exámenes y procedimientos" [cite: 238] [cite_start]con clic derecho, registrando el valor[cite: 239]. [cite_start]Los valores impactan en APAP[cite: 242].
        """
    },
    "dispositivos": {
        "contenido": """
### 💉 Dispositivos (Sondas, Vías, Catéteres)

**Ruta:**
* [cite_start]Ítem **Dispositivos/Equipos**[cite: 267].

**Pasos:**
* [cite_start]**Nuevo:** Ve a "Gráfico de dispositivos" > Nuevo dispositivo [cite: 271] > [cite_start]Elige tipo y fecha de retiro/rotación[cite: 272].
* [cite_start]**Retirar:** Clic en "Acciones de dispositivo" [cite: 274] > [cite_start]Retirar > Justificar[cite: 275, 276].
* [cite_start]**Rotar:** Clic en "Acciones de dispositivo" > Sustituir[cite: 277].
        """
    },
    "pendientes": {
        "contenido": """
### 📋 Pendientes de Enfermería

**Ruta:**
* [cite_start]Ítem **Pendientes de Enfermería**[cite: 282].

**Gestión:**
* [cite_start]**Añadir:** Botón Añadir para crear recordatorio[cite: 283].
* **Borrar/Corregir:**
    * [cite_start]Si no está liberado, puedes **Eliminar**[cite: 287].
    * [cite_start]Si ya se liberó, usa **Inactivar** justificando la acción[cite: 285].
        """
    },

    # === PERFIL MÉDICO / MULTI ===
    "agenda": {
        "contenido": """
### 📅 Gestión de Agenda (Turnos)

**Rutas:**
* [cite_start]**Agenda del día:** Historia Clínica > Consulta > Agenda de servicios[cite: 11].
* [cite_start]**Turnos libres:** Pantalla principal > Agenda de servicio[cite: 30].

**Cómo Filtrar Correctamente:**
1. [cite_start]**Por Especialidad:** Agenda de servicios > Consultar Datos > **Filtro avanzado** [cite: 32] > [cite_start]Seleccionar agendas [cite: 33, 34] > Filtrar.
2. [cite_start]**Por Profesional:** Utiliza el segmento "profesional ejecutor"[cite: 37].

**⚠️ Solución a Errores:**
* [cite_start]**"No veo nada":** Tienes que seleccionar previamente la agenda desde el filtro[cite: 13].
* [cite_start]**"Datos mezclados":** Obligatorio usar el botón **Limpiar filtros** antes de hacer una nueva búsqueda[cite: 35].
* [cite_start]**Estatus:** Luego de atender, cambia el estado de "esperando consulta" a **"ejecutada"**[cite: 27].
        """
    },
    "nota clinica": {
        "contenido": """
### 📝 Notas Clínicas (Evoluciones)

**Ruta:**
* [cite_start]Ítem **Nota Clínica**[cite: 67].

**Pasos:**
1. [cite_start]Clic en **Añadir**[cite: 68].
2. [cite_start]Elige **Tipo de nota clínica** (Tu especialidad)[cite: 69].
3. [cite_start]Escribe o usa plantillas[cite: 69].
4. [cite_start]**Liberar** para finalizar[cite: 70, 76]. [cite_start](Guardar es solo borrador [cite: 74, 75]).

**Tips:**
* [cite_start]**Alta Médica:** Usa el tipo de nota "**Resumen de HC**"[cite: 71].
* [cite_start]**Duplicar:** Clic derecho sobre nota previa > Duplicar nota clínica[cite: 80]. [cite_start](Si la nota no es tuya, es necesario borrar la firma del profesional original [cite: 81]).
* [cite_start]**Corregir:** Selecciona la nota > Clic sobre **Inactivar**[cite: 77].
        """
    },
    "informe final": {
        "contenido": """
### 🏁 Informe Final (Alta)

**Ruta:**
* [cite_start]Función **Central de informes** (desde la pantalla principal o desde el HCE usando la llamada externa)[cite: 134, 136].

**Pasos para PDF:**
1. [cite_start]**Importante:** El estatus debe ser **"realizado"**[cite: 140].
2. [cite_start]Clic derecho sobre el informe > **Ejecutar** > **Incluir interpretación PDF**[cite: 141].
3. [cite_start]Asigna el médico responsable y da OK[cite: 142].

**Enviar por Email:**
* [cite_start]Cuando el estatus cambie a "**Interpretación liberada**", haz clic derecho > Enviar > email[cite: 143].
* [cite_start]Si no hay mail cargado en el paciente, puedes usar "email electivo" o avisar a secretaría[cite: 144, 145].
        """
    },
    "cpoe": {
        "contenido": """
### 💊 CPOE y Pedidos Médicos

**Rutas:**
* [cite_start]**Ver Medicación/Indicaciones:** Árbol HCE > CPOE[cite: 104].
* [cite_start]**Justificaciones/Solicitudes:** Ítem para generar pedidos o documentos como pre-informes de psicopedagogía[cite: 83, 84].

**Pasos (Indicaciones):**
* [cite_start]**Recomendaciones:** Despliega listado > Marca el check de las deseadas > Liberar y confirmar[cite: 106, 107].
* [cite_start]**Gases Arteriales (Kinesiología):** Clic en el icono + para indicar[cite: 110].

**Pasos (Justificaciones):**
* [cite_start]Añadir > Seleccionar tipo de justificativa > Completar, guardar y liberar[cite: 85, 86].
* [cite_start]Para PDF: Selecciona el registro, haz clic en reportes > visualizar[cite: 87].
        """
    },
    "ged": {
        "contenido": """
### 📂 Gestión de Documentos (GED)

**Ruta:**
* [cite_start]Ítem **Gestión de Documentos**[cite: 125, 327].

**Uso:**
* [cite_start]**Visualizar:** Haciendo clic sobre Archivo[cite: 128, 329].
* [cite_start]**Contenido:** Contiene archivos cargados por administrativos (Anexos de la atención) y profesionales (Documentos)[cite: 126, 328].
* [cite_start]**Cargar:** Botón Añadir [cite: 129, 330] > [cite_start]Clasificar el archivo para facilitar la búsqueda[cite: 129, 330].
* [cite_start]**Ejemplo:** Para informes iniciales, elegir en tipo de archivo "informe inicial"[cite: 130].
        """
    },
    "evaluaciones": {
        "contenido": """
### 📊 Evaluaciones y Escalas

**Ruta:**
* [cite_start]Ítem **Evaluaciones**[cite: 88, 198].

**Pasos:**
1. [cite_start]Clic **Añadir** [cite: 90, 199] > [cite_start]Busca la escala deseada[cite: 94, 203].
2. Completa los campos.
3. [cite_start]**Guardar y Liberar**[cite: 95, 204].

**Tips:**
* [cite_start]**Adjuntar Imagen/Anexo:** Guarda primero (sin liberar) [cite: 97, 206][cite_start], ve a la solapa **Anexos** [cite: 98, 207][cite_start], agrega el archivo y luego Libera[cite: 98, 207].
* [cite_start]**Duplicar:** Clic derecho sobre evaluación previa > Duplicar[cite: 99, 208]. [cite_start]Luego Guardar y Liberar[cite: 100, 209].
        """
    }
}

# --- 4. MOTOR DE BÚSQUEDA ---
def buscar_solucion(consulta, rol):
    q = consulta.lower()
    
    # Búsqueda General
    if any(x in q for x in ["login", "ingresar", "usuario", "contraseña", "no veo paciente", "perfil"]): return base_de_conocimiento["login"]["contenido"]
    if any(x in q for x in ["buscar paciente", "sector", "cama", "alerta", "resumen"]): return base_de_conocimiento["navegacion"]["contenido"]
    if any(x in q for x in ["sidca", "historia vieja", "anterior", "ces", "consulta electronica"]): return base_de_conocimiento["sidca"]["contenido"]

    # Enfermería
    if rol == "Enfermería":
        if any(x in q for x in ["signos", "vitales", "presion", "temperatura", "apap", "respiratoria"]): return base_de_conocimiento["signos vitales"]["contenido"]
        if any(x in q for x in ["balance", "hidrico", "ingreso", "egreso", "liquido"]): return base_de_conocimiento["balance hidrico"]["contenido"]
        if any(x in q for x in ["adep", "administrar", "medicacion", "droga", "glucemia", "revertir"]): return base_de_conocimiento["adep"]["contenido"]
        if any(x in q for x in ["dispositivo", "sonda", "via", "cateter", "equipo"]): return base_de_conocimiento["dispositivos"]["contenido"]
        if any(x in q for x in ["pendiente", "tarea"]): return base_de_conocimiento["pendientes"]["contenido"]
    
    # Médico / Otros Profesionales
    if rol in ["Médico", "Otros profesionales"]:
        if any(x in q for x in ["agenda", "turno", "citado", "filtro", "profesional"]): return base_de_conocimiento["agenda"]["contenido"]
        if any(x in q for x in ["nota", "evolucion", "escribir", "duplicar", "plantilla", "resumen hc"]): return base_de_conocimiento["nota clinica"]["contenido"]
        if any(x in q for x in ["informe", "final", "alta", "epicrisis", "pdf", "mail", "central de informes"]): return base_de_conocimiento["informe final"]["contenido"]
        # Se agrupan CPOE y Justificaciones/Solicitudes bajo una misma clave
        if any(x in q for x in ["cpoe", "indicacion", "prescripcion", "gases", "recomendacion", "justificacion", "pedido", "solicitud", "orden"]): return base_de_conocimiento["cpoe"]["contenido"]
        if any(x in q for x in ["ged", "archivo", "adjunto", "documento", "informe inicial"]): return base_de_conocimiento["ged"]["contenido"]
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
    # Usamos una imagen de bienvenida si existe
    st.image("image_39540a.png", use_column_width="auto")
    
    st.info("👋 ¡Hola! Soy Flenisito. Para ayudarte mejor, selecciona tu perfil:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💉 Soy **Enfermero/a**", key="btn_enfermeria"):
            st.session_state.rol_usuario = "Enfermería"
            st.session_state.messages.append({"role": "assistant", "content": "Hola colega. Soy Flenisito. Pregúntame sobre **Signos Vitales, Balance, ADEP o Dispositivos**."})
            st.rerun()
            
    with col2:
        if st.button("🩺 Soy **Médico/a**", key="btn_medico"):
            st.session_state.rol_usuario = "Médico"
            st.session_state.messages.append({"role": "assistant", "content": "Hola Doctor/a. Estoy listo para guiarte en **Agenda, Notas, Informe Final y CPOE**."})
            st.rerun()

    with col3:
        if st.button("👥 **Otros profesionales**", key="btn_otros"):
            st.session_state.rol_usuario = "Otros profesionales"
            st.session_state.messages.append({"role": "assistant", "content": "¡Bienvenido/a! Soy Flenisito. Te asisto con **Agenda, Notas Clínicas, GED y Evaluaciones**."})
            st.rerun()

# CHAT
else:
    with st.sidebar:
        st.success(f"Perfil activo: **{st.session_state.rol_usuario}**")
        
        # TIPS
        st.markdown("---")
        st.markdown("### 💡 Tips Rápidos")
        st.caption("1. **Liberar** = Publicar. **Guardar** = Borrador.")
        [cite_start]st.caption("2. ¿No ves pacientes? Revisa **Sector** y **Establecimiento**[cite: 5].")
        [cite_start]st.caption("3. **SIDCA:** Clic derecho > CES[cite: 123, 325].")
        st.markdown("---")

        # ACCIONES
        if st.button("🔄 Cambiar de Perfil"):
            st.session_state.rol_usuario = None
            st.session_state.messages = []
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
                respuesta_final = respuesta_core + "\n" + MENSAJE_PIE
                st.markdown(respuesta_final)
                
                # 2. Botón de descarga (Solo si es Enfermería y el archivo existe)
                if st.session_state.rol_usuario == "Enfermería":
                    if os.path.exists(MANUAL_ENFERMERIA):
                        with open(MANUAL_ENFERMERIA, "rb") as f:
                            st.download_button(
                                label="📥 Descargar Manual de Enfermería Completo",
                                data=f,
                                file_name="Manual_Enfermeria_Tasy.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"descarga_{datetime.now().timestamp()}" # Key única para evitar errores
                            )
                    # else:
                        # Opcional: Mensaje debug si te olvidas de subir el archivo
                        # st.warning("Admin: Falta subir el archivo 'manual enfermeria (2).docx'")
                        pass

                # 3. Log
                log_interaction(st.session_state.rol_usuario, prompt, respuesta_core)
        
        st.session_state.messages.append({"role": "assistant", "content": respuesta_final})
