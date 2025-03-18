from fastapi import FastAPI, HTTPException
from react_agent.graph import question_agent, chat_agent
from react_agent.state import QuestionState, MessageRequest, MessageResponse
from react_agent.utils import dict_to_messages, messages_to_dict, process_message
import logging

app = FastAPI()

@app.post("/generate_questions")
async def generate_questions(text: str, training_id: str, topic_id: str):
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
        text=text,
        questions={},
        status="start",
        training_id=training_id,
        topic_id=topic_id
    )
    
    logging.info(f"Procesando texto: {text}")
    await question_agent.ainvoke(initial_state)
    return {"status": "ok"}


@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    pass