import streamlit as st
import csv
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Flenisito - Soporte Tasy", page_icon="🏥", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .stChatMessage { border-radius: 10px; }
    .stButton button { width: 100%; border-radius: 5px; }
    h1 { color: #005490; }
    </style>
    """, unsafe_allow_html=True)

# Archivo de logs
LOG_FILE = "registro_consultas_flenisito.csv"

# --- MENSAJE DE PIE DE PÁGINA (ESTÁNDAR) ---
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

# --- 2. FUNCIONES DE BACKEND (LOGGING) ---
def log_interaction(rol, pregunta, respuesta):
    """Guarda la interacción en un CSV para análisis posterior."""
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
        
        **Ruta:** https://tasy.fleni.org.ar/#/login
        
        **Solución a "No veo pacientes/opciones":**
        Verifica en la esquina superior derecha:
        1.  **Establecimiento:** ¿Estás en Belgrano o Escobar?
        2.  **Perfil:** ¿Es el correcto (Hospitalización Multi vs Enfermería)?
        3.  **Sector:** Debes elegir el sector en el filtro para visualizar camas.
        """
    },
    "navegacion": {
        "contenido": """
        ### 🧭 Navegación y Pacientes
        
        **Búsqueda de Pacientes:**
        * **Por Sector:** "Perspectiva Clínica" > Elegir sector > Ver listado de camas.
        * **Por Nombre/HC:** Usar el buscador por nombre o número de atención.
        * **Ingreso a HCE:** Doble clic sobre el nombre del paciente.
        
        **Alertas:**
        Al ingresar, verás alertas de seguridad (Aislamiento, Alergias). Se pueden cerrar con la X.
        """
    },
    "sidca": {
        "contenido": """
        ### 🕰️ Consulta Histórica (Sistema Anterior - SIDCA)
        
        Si necesitas ver registros antiguos que no están en Tasy:
        1.  En cualquier parte de la HCE (fondo blanco), haz **clic derecho**.
        2.  Selecciona **CES - Consulta Electrónica de Salud**.
        3.  Esto te dirige a SIDCA para ver la historia clínica vieja.
        """
    },

    # === PERFIL ENFERMERÍA ===
    "signos vitales": {
        "contenido": """
        ### 🩺 Signos Vitales y APAP (Enfermería)
        
        **1. Carga de Datos:**
        * Solapa **Signos Vitales** > Botón **Añadir**.
        * Completa los campos y la hora real del control.
        * **CRUCIAL:** Para que se vea en la grilla general, marca el check **APAP** al cargar.
        
        **2. Guardar vs. Liberar:**
        * **Guardar:** Es un borrador. Nadie más lo ve. Estado "no liberado".
        * **Liberar:** Publica el dato. Visible para todos. No editable.
        
        **3. Corregir Error:**
        * Si liberaste con error: Selecciona registro > **Inactivar** > Justificar motivo.
        """
    },
    "balance hidrico": {
        "contenido": """
        ### 💧 Balance Hídrico
        
        **Visualización:** Solapa "Análisis de balance" (Izquierda: Total | Medio: Turno | Derecha: Detalle).




