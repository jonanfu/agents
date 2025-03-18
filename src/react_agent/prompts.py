"""Default prompts used by the agent."""

SYSTEM_PROMPT = """
    Eres un asistente de IA que ayuda a los usuarios a aprender sobre un tema específico.
    Siempre debes responder en español.
"""


QUESTION_PROMPT = """
       Genera un conjunto de preguntas 5 de selección múltiple en formato JSON basado en el siguiente tema:

        Tema: {text}

        El JSON debe seguir exactamente esta estructura:

        {{
            "id": "{uuid}",
            "TrainingID": "{training_id}",
            "TopicID": "{topic_id}"	,
            "Questions": [
        {{
            "QuestionID": <Número incremental de la pregunta>,
            "Question": "<Texto de la pregunta>",
            "Options": [
                "<Opción 1>",
                "<Opción 2>",
                "<Opción 3>",
                "<Opción 4>"
            ],
            "CorrectAnswer": <Índice de la opción correcta (0-3)>
            }},
        ...
        ]
    }}

    - Reglas para la generación de preguntas:
    - Debe haber al menos 3 preguntas relacionadas con el tema.
    - Cada pregunta debe tener exactamente 4 opciones.
    - Solo una opción debe ser la correcta, representada por su índice en la lista (0-3).
    - Las preguntas deben ser claras, relevantes y de nivel intermedio o avanzado según el tema.

    No incluyas texto adicional fuera del JSON.

    El JSON debe ser válido y cumplir con la estructura especificada.
"""

TOPICS_PROMPT = """
    Explica el tema "{topic}" en un formato Markdown que pueda ser renderizado en Streamlit. 
    La explicación debe ser clara y estructurada con secciones, títulos y ejemplos de código cuando sea relevante.
    
    Formato esperado:
    - Usa encabezados con `##` o `###` para dividir las secciones.
    - Si el tema incluye código, usa bloques con triple comilla invertida (` ```python ... ``` `).
    - Usa listas, negritas y cursivas cuando sea útil para mejorar la comprensión.
    
    Ejemplo de salida esperada para "Decoradores en Python":
    
    ```
    ## 👉 Qué son los Decoradores en Python
    Los **decoradores** son funciones que modifican el comportamiento de otras funciones o métodos sin alterar su código fuente. Se usan para agregar funcionalidades como logging, control de acceso, validación de datos, etc.

    ---

    ## 👉 Ejemplo Básico
    ```python
    def mi_decorador(func):
        def envoltura():
            print("Antes de ejecutar la función")
            func()
            print("Después de ejecutar la función")
        return envoltura

    @mi_decorador
    def saludar():
        print("Hola!")

    saludar()
    ```
    **Salida:**
    ```
    Antes de ejecutar la función
    Hola!
    Después de ejecutar la función
    ```
    ```

    Devuelve solo el texto en formato Markdown sin explicaciones adicionales.
    """

