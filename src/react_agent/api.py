from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from react_agent.graph import question_agent, topics_agent, feedback_agent, content_agent
from react_agent.state import QuestionState, TopicsState, FeedbackState, GenerateTopicsState
import logging
from typing import List, Dict, Any
import traceback

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

class TopicsRequest(BaseModel):
    training_name: str
    description: str
    url: str

class FeedbackRequest(BaseModel):
    cuestionario: Dict[str, Any]


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


@app.post("/generate_topics")
async def generate_topics(request: TopicsRequest):
    """
    Genera topics para un texto dado.
    """
    try:
        # Estado inicial
        initial_state = GenerateTopicsState(
            training_name=request.training_name,
            description=request.description,
            url=request.url,
            status="start",
            topics_list=[],
            topics_json=[]
        )
        
        # Invocación del agente de contenido
        final_state = await content_agent.ainvoke(initial_state)

        return {
            "topics_json": final_state["topics_json"]
        }

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Ocurrió un error inesperado: {e}\nTraceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.post("/generate_feedback")
async def generate_feedback(cuestionarioData: Dict):
    """
    Genera feedback para un cuestionario dado.
    """
    initial_state = FeedbackState(
        cuestionario=cuestionarioData,
        status="start"
    )

    final_state = await feedback_agent.ainvoke(initial_state)
    return {
        "feedback": final_state["feedback"]
    }

