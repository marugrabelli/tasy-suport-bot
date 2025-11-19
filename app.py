import streamlit as st

# --- CONTENIDO DE LOS MANUALES (BACK-END) ---

TASY_DATA = {
    "Login": [
        [cite_start]"URL: https://tasy.fleni.org.ar/#/login [cite: 2]",
        [cite_start]"Colocamos nuestro usuario y contraseña [cite: 3]",
        [cite_start]"Verificar siempre estar en el establecimiento (Belgrano/ Escobar), sector correspondiente y perfil designado (Hospitalización Multi/Enfermeria) [cite: 5, 153]",
        [cite_start]"Sin esos datos no voy a poder visualizar pacientes y/o registrar. [cite: 6, 154]"
    ],
    "Visualizar Pacientes": [
        [cite_start]"Otra forma de visualizar pacientes es utilizando Panel de perspectiva clínica. [cite: 20]",
        [cite_start]"Elegimos el sector y podemos ver más detalles desplazando hacia la derecha. [cite: 21, 22]",
        [cite_start]"Para ver la agenda personal: Desde historia clínica, consulta, agenda de servicios. [cite: 11]",
        [cite_start]"Se pueden buscar pacientes por número de atención o nombre. [cite: 24]"
    ],
    "Nota Clínica / Evolución": [
        [cite_start]"En el ítem Nota Clínica se puede generar una nota clínica o consultar notas clínicas previas utilizando el filtro. [cite: 67]",
        [cite_start]"Para una nueva nota, haz clic en 'Añadir'. [cite: 68]",
        [cite_start]"Si quieres utilizar plantillas, selecciona desde 'tipo de nota clínica' la especialidad. [cite: 69, 301]",
        [cite_start]"Recuerda siempre 'Guardar' y 'Liberar' para finalizar la nota clínica, de lo contrario no quedará visible ni efectiva para el resto de los profesionales. [cite: 70, 75, 76, 303, 306]"
    ],
    "APAP (Signos Vitales y Balance Hídrico)": [
        [cite_start]"APAP (Análisis de parámetros asistenciales) es un ítem de visualización. [cite: 52, 53, 246, 247]",
        [cite_start]"Aquí se ve lo que se haya cargado en signos vitales y balance hídrico (si se hizo clic en APAP al cargar el registro). [cite: 53, 247]",
        [cite_start]"Para cargar Balance Hídrico, ve a la solapa 'Ingresos y egresos', haz clic en 'Añadir', selecciona el grupo y tipo, y finaliza. [cite: 257, 258, 264]",
        [cite_start]"Para cargar Signos Vitales, haz clic en 'Añadir', rellena los campos y da clic en 'APAP' si quieres que se visualice allí, luego 'Liberar'. [cite: 185, 188, 191]"
    ],
    "ADEP (Administración de Medicación)": [
        [cite_start]"ADEP muestra los horarios de medicación pendiente de administrar (lado derecho). [cite: 212, 213]",
        [cite_start]"Para registrar la administración de medicación, haz clic derecho y selecciona 'Administrar / revertir evento'. [cite: 219]",
        [cite_start]"Los valores registrados de glucemia que se carguen en ADEP impactan en APAP y Signos Vitales. [cite: 242]",
        [cite_start]"Las recomendaciones se marcan como realizadas y se pueden agregar comentarios si corresponde. [cite: 232]"
    ],
    "Evaluaciones / Escalas": [
        [cite_start]"Este ítem permite realizar escalas y ver las que hayan realizado otros profesionales. [cite: 89, 198]",
        [cite_start]"Para realizar una nueva evaluación, haz clic en 'Añadir' y selecciona la evaluación que desees. [cite: 90, 94, 199, 203]",
        [cite_start]"Si necesitas agregar archivos/imágenes, primero 'Guarda' sin liberar, ve a la solapa 'Anexos', agrega el archivo y luego 'Libera' la evaluación. [cite: 98, 207]"
    ],
    "Diagnósticos": [
        [cite_start]"En el perfil multiprofesional, solamente se pueden visualizar los diagnósticos, no se podrán editar. [cite: 118]"
    ],
    "Antecedentes de salud": [
        [cite_start]"Es un ítem de visualización donde encontrarás los antecedentes que el médico o enfermero haya cargado. [cite: 63, 288]",
        [cite_start]"Puedes visualizar y agregar antecedentes de salud, eligiendo la solapa deseada y haciendo clic en añadir. [cite: 289, 290]",
        [cite_start]"Al hacer clic en 'exhibir en alertas del paciente', este dato se visualizará en el pop up de alertas al ingresar por primera vez a la HCE. [cite: 293]",
        [cite_start]"En el caso de alergias o errores, el registro se inactiva y justifica la acción si ya fue liberado. [cite: 299]"
    ],
    "Informe Final": [
        [cite_start]"Para realizar el informe final, se utiliza la función 'central de informes'. [cite: 134]",
        [cite_start]"Para que se envíe manualmente el informe al paciente, el estatus tiene que ser 'en interpretación liberada' (que ya tiene adjunto el informe). [cite: 143]",
        [cite_start]"Si no se visualiza que el paciente tiene mail cargado, avisar a secretaría. [cite: 144]"
    ],
    "Errores/Inactivar": [
        [cite_start]"Si necesitas inactivar una Nota Clínica, selecciónala y haz clic en inactivar, justificando el motivo. [cite: 77, 307]",
        [cite_start]"En caso de error en Signos Vitales o Pendientes de Enfermería, selecciona el registro e inactiva justificando la acción. [cite: 196, 285]",
        [cite_start]"El registro no se pierde, queda inactivado con su correspondiente justificación. [cite: 78, 308]"
    ]
}

def buscar_en_manual(consulta):
    """
    Busca palabras clave en la consulta del usuario y devuelve la información relevante.
    """
    consulta_lower = consulta.lower()
    resultados = []
    
    # Mapeo de palabras clave a temas
    mapeo_palabras_clave = {
        ("login", "ingresar", "url"): "Login",
        ("pacientes", "agenda", "camas", "listado"): "Visualizar Pacientes",
        ("nota clínica", "evolución", "evolucionar", "plantilla", "liberar"): "Nota Clínica / Evolución",
        ("apap", "signos vitales", "balance hídrico", "bh"): "APAP (Signos Vitales y Balance Hídrico)",
        ("adep", "medicación", "medicar", "glucemia", "administrar"): "ADEP (Administración de Medicación)",
        ("evaluaciones", "escalas", "evaluacion", "anexos"): "Evaluaciones / Escalas",
        ("diagnóstico", "diagnosticos", "editar diagnosticos"): "Diagnósticos",
        ("informe final", "informe de alta", "central de informes"): "Informe Final",
        ("antecedentes", "alergias", "alerta", "cirugías"): "Antecedentes de salud",
        ("error", "inactivar", "eliminar", "justificar"): "Errores/Inactivar"
    }

    # 1. Buscar temas coincidentes
    temas_encontrados = set()
    for palabras, tema in mapeo_palabras_clave.items():
        if any(palabra in consulta_lower for palabra in palabras):
            temas_encontrados.add(tema)

    # 2. Recolectar la información para los temas encontrados
    for tema in temas_encontrados:
        resultados.append(f"## 📌 Tema: {tema}")
        for info in TASY_DATA.get(tema, []):
            resultados.append(f"{info}")

    if not resultados:
        return "Disculpa, no encontré información específica para esa consulta. Por favor, intenta con palabras clave más generales como: 'login', 'ADEP', 'APAP', 'nota clínica', 'evaluaciones', o 'pacientes'."
    
    return "\n".join(resultados)

# --- CONFIGURACIÓN DE LA INTERFAZ (FRONT-END) ---

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

# Pie de página
st.markdown("---")
st.caption("Hecho con Streamlit y Python.")
