import streamlit as st
#import pandas as pd

st.title("¡El Bot Funciona! (TEST DE CARGA)")
st.success("Si ves este mensaje, significa que Streamlit está operando correctamente en tu celular/PC.")

# --- CONTENIDO DE LOS MANUALES PARA LA BÚSQUEDA (BACK-END) ---

# NOTA: Para este ejemplo inicial, el contenido está simplificado y estructurado en diccionarios.
# En una versión avanzada, usaríamos un modelo de lenguaje para buscar en el texto crudo.
TASY_DATA = {
    "Login": [
        "URL: https://tasy.fleni.org.ar/#/login",
        "Colocamos nuestro usuario y contraseña",
        "Verificar siempre estar en el establecimiento (Belgrano/ Escobar), sector correspondiente y perfil designado (Hospitalización Multi / Enfermeria)",
        "Sin esos datos no voy a poder visualizar pacientes y/o registrar."
    ],
    "Visualizar Pacientes": [
        "Se puede usar Panel de perspectiva clínica, eligiendo el sector.",
        "Para ver la agenda personal: Desde historia clínica, consulta, agenda de servicios.",
        "Otra forma: Buscar en la solapa sector el listado de pacientes y al seleccionarlo del lado derecho se ingresa a la historia clínica con doble clic."
    ],
    "Nota Clínica / Evolución": [
        "En el ítem Nota Clínica se puede generar una nota clínica o consultar previas.",
        "Para una nueva nota, haz clic en 'Añadir'.",
        "Si necesitas usar plantillas, selecciona desde 'tipo de nota clínica' la especialidad.",
        "Siempre debes 'Guardar' y 'Liberar' para que la nota sea visible y efectiva para el resto de los profesionales."
    ],
    "APAP (Signos Vitales y Balance Hídrico)": [
        "APAP (Análisis de parámetros asistenciales) es un ítem de visualización.",
        "Enfermería carga los datos en Signos Vitales y Balance Hídrico.",
        "Para cargar Signos Vitales, haz clic en 'Añadir' en la solapa 'Signos Vitales', completa los campos y da clic en 'APAP' si quieres que se visualice allí, luego 'Liberar'.",
        "Para cargar Balance Hídrico, ve a la solapa 'Ingresos y egresos', haz clic en 'Añadir', selecciona grupo/tipo y finaliza."
    ],
    "ADEP (Administración de Medicación)": [
        "ADEP muestra los horarios de medicación pendiente de administrar.",
        "Para registrar la administración de medicación, haz clic derecho y selecciona 'Administrar / revertir evento'.",
        "También puedes marcar Recomendaciones como realizadas y agregar comentarios si corresponde.",
        "Los valores registrados de glucemia que se carguen en ADEP impactan en APAP y Signos Vitales."
    ],
    "Evaluaciones / Escalas": [
        "Este ítem permite realizar escalas y ver las de otros profesionales.",
        "Para una nueva, haz clic en 'Añadir'.",
        "Si necesitas agregar archivos/imágenes a la evaluación, primero 'Guarda' sin liberar, ve a la solapa 'Anexos', agrega el archivo y luego 'Libera' la evaluación.",
    ],
    "Diagnósticos": [
        "En el perfil multiprofesional, solamente se pueden visualizar los diagnósticos, no se podrán editar."
    ]
}

def buscar_en_manual(consulta):
    """
    Busca palabras clave en la consulta del usuario y devuelve la información relevante.
    """
    consulta_lower = consulta.lower()

    resultados = []

