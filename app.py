import streamlit as st

# --- CONTENIDO DE LOS MANUALES (BACK-END) ---

TASY_DATA = {
    "Login": [
        "URL: https://tasy.fleni.org.ar/#/login",
        "Colocamos nuestro usuario y contraseña",
        "Verificar siempre estar en el establecimiento (Belgrano/ Escobar), sector correspondiente y perfil designado (Hospitalización Multi/Enfermeria)",
        "Sin esos datos no voy a poder visualizar pacientes y/o registrar."
    ],
    "Visualizar Pacientes": [
        "Se puede usar Panel de perspectiva clínica, eligiendo el sector.",
        "Para ver la agenda personal: Desde historia clínica, consulta, agenda de servicios.",
        "Otra forma: Buscar en la solapa sector el listado de pacientes y al seleccionarlo del lado derecho se ingresa a la historia clínica con doble clic.",
        "Se pueden buscar pacientes por número de atención o nombre."
    ],
    "Nota Clínica / Evolución": [
        "En el ítem Nota Clínica se puede generar una nota clínica o consultar notas clínicas previas utilizando el filtro.",
        "Para una nueva nota, haz clic en 'Añadir'.",
        "Si quieres utilizar plantillas, selecciona desde 'tipo de nota clínica' la especialidad.",
        "Recuerda siempre 'Guardar' y 'Liberar' para finalizar la nota clínica, de lo contrario no quedará visible ni efectiva para el resto de los profesionales."
    ],
    "APAP (Signos Vitales y Balance Hídrico)": [
        "APAP (Análisis de parámetros asistenciales) es un ítem de visualización.",
        "Aquí se ve lo que se haya cargado en signos vitales y balance hídrico (si se hizo clic en APAP al cargar el registro).",
        "Para cargar Balance Hídrico, ve a la solapa 'Ingresos y egresos', haz clic en 'Añadir', selecciona el grupo y tipo, y finaliza.",
        "Para cargar Signos Vitales, haz clic en 'Añadir', rellena los campos y da clic en 'APAP' si quieres que se visualice allí, luego 'Liberar'."
    ],
    "ADEP (Administración de Medicación)": [
        "ADEP muestra los horarios de medicación pendiente de administrar (lado derecho).",
        "Para registrar la administración de medicación, haz clic derecho y selecciona 'Administrar / revertir evento'.",
        "Los valores registrados de glucemia que se carguen en ADEP impactan en APAP y Signos Vitales.",
        "Las recomendaciones se marcan como realizadas y se pueden agregar comentarios si corresponde."
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
        "Es un ítem de visualización donde encontrarás los antecedentes que el médico o enfermero haya cargado.",
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

def buscar_en_manual(consulta):
    """
    Busca palabras clave en la consulta del usuario y devuelve la información relevante.
    """
