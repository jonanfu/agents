"""Utility & helper functions."""
import uuid
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from react_agent.prompts import QUESTION_PROMPT
from react_agent.state import QuestionState
from azure.cosmos import CosmosClient
from typing import List, Dict, Any
from langchain_openai import AzureChatOpenAI
from react_agent.configuration import Config
import json
import logging


config = Config()

def generate_questions(state: QuestionState, model: AzureChatOpenAI) -> Dict[str, Any] :
    """Generar pregunta de seleccion multiple"""
    try:
        prompt = QUESTION_PROMPT.format(text=state["text"], uuid=str(uuid.uuid4()), training_id=state["training_id"], topic_id=state["topic_id"])
        response = model.invoke(prompt)
        logging.info(response)

        if not response or not response.content:
            print("No se recibió respuesta del modelo")
            return {"messages": "No se recibió respuesta del modelo"}
            
        content = response.content
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Error al generar preguntas: {str(e)}")
        return {"messages": f"Error al generar preguntas: {str(e)}"}


def save_to_cosmos(state: QuestionState):
    """Guarda las preguntas en Cosmos DB."""
    client = CosmosClient(config.COSMOS_ENDPOINT, credential=config.COSMOS_KEY)
    database = client.get_database_client(config.COSMOS_DATABASE_NAME)
    container = database.get_container_client(config.COSMOS_CONTAINER_NAME)
    
    try:
        container.create_item(state["questions"])
        return QuestionState(text=state["text"], questions=state["questions"], status="saved")
    except Exception as e:
        logging.error(f"Error al guardar en Cosmos DB: {str(e)}")
        return QuestionState(text=state.text, questions=state.questions, status="error")


