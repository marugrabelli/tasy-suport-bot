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
* **👤 Perfil:** Verifica que tu **Log In** esté en el **establecimiento y perfil correcto** (Ej: Hospitalización Multi/Enfermería).
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
* **Ver Camas:** Función "Perspectiva Clínica" > Elegir sector.
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
3. Se abrirá la ventana de SIDCA para ver evoluciones viejas.
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

**⚠️ Solución a Errores:**
* **Guardar vs Liberar:**
    * *Guardar:* Es borrador (nadie más lo ve).
    * *Liberar:* Publicar (visible para todos).
* **Corregir:** Si liberaste mal, selecciona el registro > **Inactivar** > Justificar motivo.
        """
    },
    "balance hidrico": {
        "contenido": """
### 💧 Balance Hídrico

**Ruta:**
* Solapa **Ingresos y Egresos**.

**Pasos para Cargar:**
1. Clic en **Añadir**.
2. Lado Izquierdo: Elige el Grupo y Tipo de líquido.
3. **CRUCIAL:** Clic en la **Flecha Derecha (➡️)** para pasarlo al panel de carga.
4. Se abre una ventana: pon el volumen y confirma con **Finalizar**.

**Visualización:**
* Ve a la solapa "Análisis de balance" para ver los totales por turno.
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
3. Agrega comentario si hace falta y da OK.

**Casos Especiales:**
* **Medicación Suspendida:** Usa el filtro arriba y marca "medicación suspendida".
* **Glucemia:** Se carga en "Exámenes y procedimientos" con clic derecho.
        """
    },
    "dispositivos": {
        "contenido": """
### 💉 Dispositivos (Sondas, Vías, Catéteres)

**Ruta:**
* Ítem **Dispositivos/Equipos**.

**Pasos:**
* **Nuevo:** Ve a "Gráfico de dispositivos" > Nuevo dispositivo > Elige tipo y fecha de retiro.
* **Retirar:** Clic en "Acciones de dispositivo" > Retirar > Justificar.
* **Rotar:** Clic en "Acciones de dispositivo" > Sustituir.
        """
    },
    "pendientes": {
        "contenido": """
### 📋 Pendientes de Enfermería

**Ruta:**
* Ítem **Pendientes de Enfermería**.

**Gestión:**
* **Añadir:** Botón Añadir para crear recordatorio.
* **Borrar:** Si no está liberado, usa Eliminar. Si ya se liberó, usa Inactivar.
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
1. **Por Especialidad:** Agenda de servicios > Consultar Datos > **Filtro avanzado** > Seleccionar agendas > Filtrar.
2. **Por Profesional:** Usa la lupa en el campo "Profesional ejecutor".

**⚠️ Solución a Errores:**
* **"No veo nada":** El sistema no muestra datos si no seleccionas la agenda en el filtro primero.
* **"Datos mezclados":** Obligatorio usar el botón **Limpiar filtros** antes de hacer una nueva búsqueda.
        """
    },
    "nota clinica": {
        "contenido": """
### 📝 Notas Clínicas (Evoluciones)

**Ruta:**
* Ítem **Nota Clínica**.

**Pasos:**
1. Clic en **Añadir**.
2. Elige **Tipo de nota clínica** (Tu especialidad).
3. Escribe o usa plantillas.
4. **Liberar** para finalizar.

**Tips:**
* **Alta Médica:** Usa el tipo de nota "Resumen de HC".
* **Duplicar:** Clic derecho sobre nota vieja > Duplicar. (¡Borra la firma del original!).
        """
    },
    "informe final": {
        "contenido": """
### 🏁 Informe Final (Alta)

**Ruta:**
* Función **Central de informes**.

**Pasos para PDF:**
1. Verifica que el estatus sea **"Realizado"**.
2. Clic derecho sobre el informe > **Ejecutar** > **Incluir interpretación PDF**.
3. Asigna el médico responsable y da OK.

**Enviar por Email:**
* Cuando el estatus cambie a "Interpretación liberada", haz clic derecho > Enviar > Email.
        """
    },
    "cpoe": {
        "contenido": """
### 💊 CPOE y Pedidos Médicos

**Rutas:**
* **Ver Medicación:** Árbol HCE > CPOE.
* **Hacer Pedidos:** Ítem **Justificaciones/Solicitudes**.

**Pasos:**
* **Indicaciones:** Despliega listado > Marca checks > Liberar y confirmar.
* **Pedidos (Estudios/Interconsultas):** Añadir > Elegir tipo > Completar > Guardar y Liberar.
        """
    },
    "ged": {
        "contenido": """
### 📂 Gestión de Documentos (GED)

**Ruta:**
* Ítem **Gestión de Documentos**.

**Uso:**
* **Visualizar:** Doble clic sobre el archivo para ver PDFs externos o escaneos de admisión.
* **Cargar:** Botón Añadir > Clasifica bien el tipo de archivo para encontrarlo luego.
        """
    },
    "evaluaciones": {
        "contenido": """
### 📊 Evaluaciones y Escalas

**Ruta:**
* Ítem **Evaluaciones**.

**Pasos:**
1. Clic Añadir > Busca la escala deseada.
2. Completa los campos.
3. **Guardar y Liberar**.

**Tip:**
* Si necesitas adjuntar una foto a la evaluación, Guarda primero (sin liberar), ve a la solapa Anexos, sube la foto y luego Libera.
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
    if any(x in q for x in ["signos", "vitales", "presion", "temperatura", "apap", "respiratoria"]): return base_de_conocimiento["signos vitales"]["contenido"]
    if any(x in q for x in ["balance", "hidrico", "ingreso", "egreso", "liquido"]): return base_de_conocimiento["balance hidrico"]["contenido"]
    if any(x in q for x in ["adep", "administrar", "medicacion", "droga", "glucemia", "revertir"]): return base_de_conocimiento["adep"]["contenido"]
    if any(x in q for x in ["dispositivo", "sonda", "via", "cateter", "equipo"]): return base_de_conocimiento["dispositivos"]["contenido"]
    if any(x in q for x in ["pendiente", "tarea"]): return base_de_conocimiento["pendientes"]["contenido"]

    # Multi
    if any(x in q for x in ["agenda", "turno", "citado", "filtro"]): return base_de_conocimiento["agenda"]["contenido"]
    if any(x in q for x in ["nota", "evolucion", "escribir", "duplicar", "plantilla"]): return base_de_conocimiento["nota clinica"]["contenido"]
    if any(x in q for x in ["informe", "final", "alta", "epicrisis", "pdf", "mail"]): return base_de_conocimiento["informe final"]["contenido"]
    if any(x in q for x in ["cpoe", "indicacion", "prescripcion", "gases", "recomendacion"]): return base_de_conocimiento["cpoe"]["contenido"]
    if any(x in q for x in ["justificacion", "pedido", "solicitud", "orden"]): return base_de_conocimiento["cpoe"]["contenido"]
    if any(x in q for x in ["ged", "archivo", "adjunto", "documento"]): return base_de_conocimiento["ged"]["contenido"]
    if any(x in q for x in ["evaluacion", "escala", "score", "imagen"]): return base_de_conocimiento["evaluaciones"]["contenido"]

    # Default
    msg = "⚠️ No encuentro una ruta exacta para esa consulta en los manuales.\n\n"
    if rol == "Enfermería":
        msg += "Temas disponibles: **Signos Vitales, Balance Hídrico, ADEP, Glucemia, Dispositivos, Pendientes**."
    else:
        msg += "Temas disponibles: **Agenda, Notas Clínicas, Informe Final, CPOE, Justificaciones, GED**."
    return msg

# --- 5. INTERFAZ DE USUARIO ---

st.title("🏥 Flenisito")
st.markdown("**Tu Asistente Virtual para Tasy en FLENI**")

if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ONBOARDING
if st.session_state.rol_usuario is None:
    st.info("👋 ¡Hola! Soy Flenisito. Para ayudarte mejor, selecciona tu perfil:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💉 Soy Enfermería"):
            st.session_state.rol_usuario = "Enfermería"
            st.session_state.messages.append({"role": "assistant", "content": "Hola colega. Soy Flenisito. Pregúntame sobre **Signos Vitales, Balance, ADEP o Dispositivos**."})
            st.rerun()
    with col2:
        if st.button("🩺 Soy Médico / Multi"):
            st.session_state.rol_usuario = "Médico / Multi"
            st.session_state.messages.append({"role": "assistant", "content": "Hola Doctor/a. Soy Flenisito. Estoy listo para guiarte en **Agenda, Notas, Informe Final y CPOE**."})
            st.rerun()

# CHAT
else:
    with st.sidebar:
        st.success(f"Perfil: **{st.session_state.rol_usuario}**")
        
        # TIPS
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
                    else:
                        # Opcional: Mensaje debug si te olvidas de subir el archivo
                        # st.warning("Admin: Falta subir el archivo 'manual enfermeria (2).docx'")
                        pass

                # 3. Log
                log_interaction(st.session_state.rol_usuario, prompt, respuesta_core)
        
        st.session_state.messages.append({"role": "assistant", "content": respuesta_final})

