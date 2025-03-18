from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from react_agent.graph import question_agent, topics_agent
from react_agent.state import QuestionState, TopicsState#, MessageRequest, MessageResponse
#from react_agent.utils import dict_to_messages, messages_to_dict, process_message
import logging

app = FastAPI()

# Definir el modelo Pydantic para el request
class QuestionRequest(BaseModel):
    text: str
    training_id: str
    topic_id: str

class ChatRequest(BaseModel):
    topic: str = Field(..., description="El tema sobre el que se pregunta")
    question: str | None = Field(None, description="La pregunta opcional dentro del tema")
    id_user: str

@app.post("/generate_questions")
async def generate_questions(request: QuestionRequest):
    """
    Genera preguntas de selección múltiple para un texto dado.

    Args:
        text (str): El texto del que se generarán las preguntas.
        training_id (str): El ID del entrenamiento.
        topic_id (str): El ID del tema.

    Returns:
        response: ok
    """ 
    initial_state = QuestionState(
        text=request.text,
        questions={},
        status="start",
        training_id=request.training_id,
        topic_id=request.topic_id
    )

    # Ejecutar el agente y obtener el estado final
    final_state = await question_agent.ainvoke(initial_state)

    # Retornar las preguntas generadas
    return {
        "status": final_state["status"],
        "questions": final_state["questions"]
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Maneja la interacción con el usuario:
    - Si solo se envía `topic`, devuelve la explicación del tema.
    - Si se envía `topic` y `question`, responde en el contexto del tema.
    """
    initial_state = TopicsState(
        topic=request.topic,
        status="chatbot" if request.question else "initialize",
        response="",
        question=request.question if request.question else None,
        id_user=request.id_user,
        messages=[]  # Inicializamos messages como una lista vacía si no existe
    )

    logging.info(f"Procesando request: {initial_state}")
    print(f"Procesando request: {initial_state}")

    final_state = await topics_agent.ainvoke(initial_state)
    return {
        "topic": request.topic,
        "question": request.question,
        "response": final_state["response"]
    }
