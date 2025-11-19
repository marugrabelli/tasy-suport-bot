import streamlit as st

# --- 1. BASE DE DATOS DE CONOCIMIENTO (TASY_DATA) ---

TASY_DATA = {
    "Login": [
        "URL: https://tasy.fleni.org.ar/#/login",
        "Colocamos nuestro usuario y contraseña",
        "Verificar siempre estar en el establecimiento (Belgrano/ Escobar), sector correspondiente y perfil designado (Hospitalización Multi/Enfermeria).",
        "Sin esos datos no voy a poder visualizar pacientes y/o registrar."
    ],
    "Visualizar Pacientes": [
        "Utilizar Panel de perspectiva clínica y elegir el sector.",
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
        "Para cargar Balance Hídrico, ve a la solapa 'Ingresos y egresos' y haz clic en 'Añadir'."
    ],
    "ADEP (Administración de Medicación)": [
        "ADEP muestra los horarios de medicación pendiente de administrar.",
        "Para registrar la administración, haz clic derecho y selecciona 'Administrar / revertir evento'.",
        "Los valores registrados de glucemia en ADEP impactan en APAP y Signos Vitales."
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
    Busca palabras clave en la consulta del usuario y devuelve la información relevante del diccionario TASY_DATA.
    """
    consulta_lower = consulta.lower()
    resultados = []
    
    # Mapeo de palabras clave a temas
    mapeo_palabras_clave = {
        ("login", "ingresar", "url"): "Login",
        ("pacientes", "agenda", "camas", "listado", "perspectiva clínica"): "Visualizar Pacientes",
        ("nota clínica", "evolución", "evolucionar", "plantilla", "liberar"): "Nota Clínica / Evolución",
        ("apap", "signos vitales", "balance hídrico", "bh"): "APAP (Signos Vitales y Balance Hídrico)",
        ("adep", "medicación", "medicar", "glucemia", "administrar", "revertir evento"): "ADEP (Administración de Medicación)",
        ("error", "inactivar", "eliminar", "justificar"): "Errores/Inactivar"
    }

    temas_encontrados = set()
    for palabras, tema in mapeo_palabras_clave.items():
        if any(palabra in consulta_lower for palabra in palabras):
            temas_encontrados.add(tema)

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
st.subheader("Asistente Virtual de Hospitalización")
st.markdown("Escribe tu pregunta y te ayudaré a encontrar la información clave en los manuales de **Hospitalización Multi** y **Enfermería**.")

# Interacción del Usuario
consulta_usuario = st.text_input("Ingresa tu pregunta sobre Tasy (ej: ¿Cómo cargo el Balance Hídrico? o ¿Cómo libero la nota clínica?)")

if consulta_usuario:
    st.info(f"Buscando respuesta para: **{consulta_usuario}**")
    
    # Llama a la función de lógica
    respuesta_bot = buscar_en_manual(consulta_usuario)
    
    # Muestra la respuesta del bot
    st.success("Respuesta del Bot Basada en Manuales:")
    st.markdown(respuesta_bot)

st.markdown("---")
st.caption("Hecho con Streamlit y Python.")
