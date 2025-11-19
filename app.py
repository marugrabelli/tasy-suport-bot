import streamlit as st
import unidecode

# --- 0. FUNCIÓN DE LIMPIEZA DE TEXTO ---
def quitar_acentos(texto):
    """Convierte el texto a minúsculas y elimina acentos (diacríticos) y la 'ñ'."""
    return unidecode.unidecode(texto).lower()

# --- 1. BASE DE DATOS DE CONOCIMIENTO (TASY_DATA) ---

TASY_DATA = {
    "Login": [
        "URL: https://tasy.fleni.org.ar/#/login",
        "Colocamos nuestro usuario y contraseña",
        "Verificar siempre estar en el establecimiento (Belgrano/ Escobar), sector correspondiente y perfil designado (Hospitalización Multi/Enfermeria).",
        "Sin esos datos no voy a poder visualizar pacientes y/o registrar."
    ],
    "Visualizar Pacientes": [
        "Se puede usar Panel de perspectiva clínica, eligiendo el sector.",
        "Para ver la agenda personal: Desde historia clínica, consulta, agenda de servicios.",
        "Se pueden buscar pacientes por número de atención o nombre."
    ],
    "Nota Clínica / Evolución": [
        "En el ítem Nota Clínica, haz clic en 'Añadir' para una nueva nota.",
        "Selecciona la especialidad desde 'tipo de nota clínica' si vas a usar plantillas.",
        "Recuerda siempre 'Guardar' y 'Liberar' para finalizar la nota clínica y hacerla visible."
    ],
    "APAP (Signos Vitales y Balance Hídrico)": [
        "APAP (Análisis de parámetros asistenciales) es un ítem de visualización (no de registro).",
        "Se visualiza lo que se cargó en signos vitales y balance hídrico (si se marcó APAP al registrar).",
        "Para cargar Balance Hídrico, ve a la solapa 'Ingresos y egresos' y haz clic en 'Añadir'.",
        "Para cargar Signos Vitales, haz clic en 'Añadir', rellena los campos y da clic en 'APAP' si quieres que se visualice allí, luego 'Liberar'."
    ],
    "ADEP (Administración de Medicación)": [
        "ADEP muestra los horarios de medicación pendiente de administrar.",
        "Para registrar la administración, haz clic derecho y selecciona 'Administrar / revertir evento'.",
        "Los valores registrados de glucemia en ADEP impactan en APAP y Signos Vitales."
    ],
    "Evaluaciones / Escalas": [
        "Este ítem permite realizar escalas y ver las que hayan realizado otros profesionales.",
        "Para realizar una nueva evaluación, haz clic en 'Añadir' y selecciona la evaluación que desees.",
        "Si necesitas agregar archivos/imágenes, primero 'Guarda' sin liberar, ve a la solapa 'Anexos', agrega el archivo y luego 'Libera' la evaluación."
    ],
    "Diagnósticos": [
        "En el perfil multiprofesional, solamente se pueden visualizar los diagnósticos, no se podrán editar.",
        "Se pueden consultar los diagnósticos de la atención y los diagnósticos históricos del paciente."
    ],
    "Antecedentes de salud": [
        "Puedes visualizar y agregar antecedentes de salud, eligiendo la solapa deseada y haciendo clic en añadir.",
        "Al hacer clic en 'exhibir en alertas del paciente', este dato se visualizará en el pop up de alertas al ingresar por primera vez a la HCE.",
        "En el caso de alergias o errores, el registro se inactiva y justifica la acción si ya fue liberado."
    ],
    "Informe Final": [
        "Para realizar el informe final, se utiliza la función 'central de informes'.",
        "Para que se envíe manualmente el informe al paciente, el estatus tiene que ser 'en interpretación liberada' (que ya tiene adjunto el informe).",
        "Si no se visualiza que el paciente tiene mail cargado, avisar a secretaría."
    ],
    "Errores/Inactivar": [
        "Si necesitas inactivar una Nota Clínica, selecciónala y haz clic sobre inactivar, justificando el motivo.",
        "En caso de error en Signos Vitales o Pendientes de Enfermería, selecciona el registro e inactiva justificando la acción.",
        "El registro no se pierde, queda inactivado con su correspondiente justificación."
    ]
}

# --- 2. LÓGICA DE BÚSQUEDA (search_logic) ---

def buscar_en_manual(consulta):
    """
    Busca palabras clave en la consulta del usuario después de normalizar (quitar acentos).
    """
    consulta_normalizada = quitar_acentos(consulta) 
    
    # Mapeo de palabras clave a temas (todas sin acentos)
    mapeo_palabras_clave = {
        ("login", "ingresar", "url"): "Login",
        ("pacientes", "agenda", "camas", "listado", "perspectiva clinica"): "Visualizar Pacientes",
        ("nota clinica", "evolucion", "evolucionar", "plantilla", "liberar"): "Nota Clínica / Evolución",
        ("apap", "signos vitales", "balance hidrico", "bh"): "APAP (Signos Vitales y Balance Hídrico)",
        ("adep", "medicacion", "medicar", "glucemia", "administrar", "revertir evento"): "ADEP (Administración de Medicación)",
        ("evaluaciones", "escalas", "evaluacion", "anexos"): "Evaluaciones / Escalas",
        ("diagnostico", "diagnosticos", "editar diagnosticos"): "Diagnósticos",
        ("informe final", "informe de alta", "central de informes"): "Informe Final",
        ("antecedentes", "alergias", "alerta", "cirugias"): "Antecedentes de salud",
        ("error", "inactivar", "eliminar", "justificar"): "Errores/Inactivar"
    }

    temas_encontrados = set()
    for palabras, tema in mapeo_palabras_clave.items():
        if any(palabra in consulta_normalizada for palabra in palabras):
            temas_encontrados.add(tema)

    resultados = []
    for tema in temas_encontrados:
        resultados.append(f"## 📌 Tema: {tema}")
        for info in TASY_DATA.get(tema, []):
            resultados.append(f"* {info}")

    if not resultados:
        return "Disculpa, no encontré información específica para esa consulta. Por favor, intenta con palabras clave más generales."
    
    return "\n".join(resultados)

# --- 3. CONFIGURACIÓN DE LA INTERFAZ (FRONT-END) ---

st.set_page_config(page_title="Soporte Tasy FLENI Bot", layout="centered")

st.title("🤖 Soporte Tasy FLENI")
st.markdown("---")
st.subheader("Asistente Virtual")
st.markdown("Escribe tu pregunta y te ayudaré a resolver dudas en Tasy.")

# Interacción del Usuario
consulta_usuario = st.text_input("Ingresa tu pregunta sobre Tasy (ej: Como cargo el balance hidrico? o Como libero la nota clinica?)")

if consulta_usuario:
    st.info(f"Buscando respuesta para: **{consulta_usuario}**")
    
    # Llama a la función de lógica
    respuesta_bot = buscar_en_manual(consulta_usuario)
    
    # Muestra la respuesta del bot
    st.success("Respuesta del Bot Basada en Manuales:")
    st.markdown(respuesta_bot)

# --- 4. PIE DE PÁGINA AMIGABLE (Mensaje de Soporte Final) ---
st.markdown("---")
st.markdown("""
### 💡 Soporte Inicial Tasy FLENI - Tips Rápidos 🚀

Antes de llamar, ¡revisa estos puntos!

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

st.caption("Hecho con Streamlit y Python.")


