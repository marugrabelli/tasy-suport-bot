# 🏥 Flenisito - Asistente de Soporte Tasy FLENI (BETA)

Este repositorio contiene el código fuente y la documentación del asistente virtual **Flenisito**, una herramienta diseñada para facilitar la transición e implementación del nuevo Sistema de Información Hospitalaria (Tasy) en FLENI.

## ✨ Propósito

El objetivo principal de Flenisito es ofrecer soporte técnico y funcional inmediato a los profesionales de la salud (Enfermería, Médicos y Otros) para que puedan resolver dudas frecuentes y problemas básicos de uso con la herramienta Tasy, promoviendo la **autosolución** y reduciendo la carga de consultas al soporte telefónico.

## 🚀 Ver el Bot en Acción

**Estado Actual:** Maqueta / Versión Beta
**Link Público:** [https://tasysoporte.streamlit.app/](https://tasysoporte.streamlit.app/)

## 💻 Arquitectura y Tecnología

El asistente está construido bajo una arquitectura ligera y centrada en la experiencia del usuario (UX):

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Frontend/Lógica** | Python (Streamlit) | Desarrolla la interfaz de usuario amigable y gestiona el flujo de la conversación (Onboarding, Tags, Respuestas). |
| **Base de Conocimiento** | JSON (`knowledge_base.json`) | Almacena de manera estructurada las plantillas de respuesta, incluyendo Título, Ruta, Acciones Clave, Errores y Soluciones. |
| **Documentación** | DOCX/Manuales | Archivos de manuales por perfil (`Manual_Medicos.docx`, `manual enfermeria (2).docx`, etc.) que el bot ofrece para descarga. |
| **Analítica** | CSV (`registro_consultas_flenisito.csv`) | Registra cada interacción y consulta libre para identificar los "hot topics" y mejorar el contenido del bot en futuras iteraciones. |

## ⚙️ Flujo de Soporte (UX)

El flujo de Flenisito está diseñado para la máxima eficiencia:

1.  **Selección de Perfil:** Se elige la profesión (Enfermería, Médico, Otros) para personalizar las opciones.
2.  **Menú de Tags:** Se presentan botones con las dudas más frecuentes, clasificados por color y tema.
3.  **Respuesta Estructurada:** La solución se presenta en un formato consistente y fácil de leer (Título, Ruta de Acceso, Acciones, Errores Comunes).
4.  **Recursos Adicionales:** Cada respuesta incluye un pie de página con tips clave (ej: "Usar Google Chrome", "Limpiar Caché") para evitar llamadas, y un botón para descargar el manual completo de la profesión.

## 🛠️ Contenido de los Archivos Clave

* **`app.py`**: Script principal de Streamlit que orquesta la aplicación.
* **`knowledge_base.json`**: Contiene todas las plantillas de respuesta estructuradas.
* **`registro_consultas_flenisito.csv`**: Log de interacciones (requiere permisos de escritura en la implementación final).
* **Manuales de Referencia**: Documentos de soporte originales de FLENI.

## 🤝 Colaboración y Estado Futuro

Este es un proyecto en fase de prueba. Agradecemos cualquier feedback sobre la precisión de las respuestas o la usabilidad de la interfaz.

---
*Desarrollado por el equipo de Soporte Tasy FLENI.*
