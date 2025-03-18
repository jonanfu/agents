"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""
import logging

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END, START
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from react_agent.utils import generate_questions, save_to_cosmos
from react_agent.state import QuestionState, TopicsState
from react_agent.configuration import Config
from react_agent.prompts import TOPICS_PROMPT, SYSTEM_PROMPT

def load_model() -> AzureChatOpenAI:
    """Load and configure the Azure OpenAI model."""
    return AzureChatOpenAI(
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
        azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
        api_version=Config.AZURE_OPENAI_API_VERSION,
        api_key=Config.AZURE_OPENAI_API_KEY,
        temperature=0.7,
    )

def estado_inicial(state: QuestionState) -> QuestionState:

    return QuestionState(text=state["text"], questions={}, status="start", training_id=state["training_id"], topic_id=state["topic_id"])

def generate_questions_node(state: QuestionState) -> QuestionState:
    """Generar preguntas de selección múltiple."""
    logging.info("Generando preguntas...")
    logging.info(state)
    nuevo_estado = state.copy()


    try:
        # Cargar el modelo
        model = load_model()

        # Crear un QuestionState temporal para pasar a la función de utils
        
        # Generar preguntas usando la función de utils
        questions = generate_questions(state, model)
        nuevo_estado["questions"] = questions

        logging.info("Preguntas generadas:")
        logging.info(questions)
        nuevo_estado["status"] = "generated"

        return nuevo_estado
    
    except Exception as e:
        logging.error(f"Error generando preguntas: {str(e)}")
        nuevo_estado["status"] = "error"
        return nuevo_estado
    


async def save_questions_node(state: QuestionState) -> QuestionState:
    """Guardar las preguntas en Cosmos DB."""
    logging.info("Guardando preguntas...")
    logging.info(state)
    nuevo_estado = state.copy()
    try:
        save_to_cosmos(state)
        nuevo_estado["status"] = "saved"
        return nuevo_estado

    except Exception as e:
        logging.error(f"Error guardando preguntas: {str(e)}")
        nuevo_estado["status"] = "error"
        return nuevo_estado

async def result_node(state: QuestionState) -> QuestionState:
    """Resultado de la generación de preguntas."""
    logging.info("Resultado de la generación de preguntas...")
    logging.info(state)
    nuevo_estado = state.copy()
    nuevo_estado["status"] = "result"
    return nuevo_estado

# Configurar flujo de ejecución
workflow = StateGraph(QuestionState)

# Agregar nodos
workflow.add_node("estado_inicial", estado_inicial)
workflow.add_node("generate_questions", generate_questions_node)  # Cambié el nombre de la función
workflow.add_node("save_questions", save_questions_node)
workflow.add_node("result", result_node)
# Configurar flujo de ejecución
workflow.add_edge(START, "estado_inicial")
workflow.add_edge("estado_inicial", "generate_questions")
workflow.add_edge("generate_questions", "save_questions")
workflow.add_edge("save_questions", "result")
workflow.add_edge("result", END)

# Compilar el grafo
question_agent = workflow.compile()
question_agent.name = "Question Generation"

# Crear el grafo
#graph.draw_mermaid_png(output_file_path="../img/question_generation.png")


# Codigo para el chat
# Función para inicializar el chatbot con el prompt del tema
def initialize_chat(state: TopicsState):
    print('entra initialize')
    model = load_model()
    prompt = TOPICS_PROMPT.format(topic=state["topic"])

    # Crear un mensaje del sistema para la generación de tópicos
    system_message = {"role": "system", "content": SYSTEM_PROMPT}
    
    # Crear un mensaje interno para solicitar tópicos (no se muestra al usuario)
    internal_message = {"role": "user", "content": prompt, "visible": False}

    # Obtener la respuesta del modelo con los tópicos
    messages = [system_message, internal_message]
    response = model.invoke(messages)

    # Crear un mensaje de asistente con los tópicos (este es el primer mensaje que ve el usuario)
    assistant_message = {
        "role": "assistant", 
        "content": response.content
    }
    
    # Inicializamos el estado con el mensaje del sistema y la respuesta del asistente
    return {
        "topic": state["topic"],
        "question": None,
        "status": "done",
        "response": response.content,
        "id_user": state["id_user"],
        "messages": [system_message, assistant_message],  # Aquí inicializamos messages
    }

# Código para el chat
def chatbot(state: TopicsState) -> TopicsState:
    print('entra chatbot')
    model = load_model()

    # Asegurar que el historial de mensajes contiene la introducción del tema
    if not state["messages"]:
        system_message = {"role": "system", "content": SYSTEM_PROMPT}
        initial_prompt = TOPICS_PROMPT.format(topic=state["topic"])
        internal_message = {"role": "user", "content": initial_prompt, "visible": False}
        response = model.invoke([system_message, internal_message])
        assistant_message = {"role": "assistant", "content": response.content}

        state["messages"] = [system_message, internal_message, assistant_message]

    # Agregar la pregunta actual al historial
    if state["question"]:
        user_message = {"role": "user", "content": state["question"]}
        state["messages"].append(user_message)

    # Invocar el modelo con el historial de mensajes
    response = model.invoke(state["messages"])
    assistant_message = {"role": "assistant", "content": response.content}
    state["messages"].append(assistant_message)

    return {
        "topic": state["topic"],
        "question": state["question"],
        "status": "done",
        "response": response.content,
        "id_user": state["id_user"],
        "messages": state["messages"],
    }


# Definir una función de decisión para el flujo
def conditional_routing(state: TopicsState):
    print(state["status"])
    return state["status"]

# Configuración del grafo de estados
workflow_topics = StateGraph(TopicsState)

# agregar nodos
workflow_topics.add_node("initialize", initialize_chat)
workflow_topics.add_node("chatbot", chatbot)

# Definir el flujo

# Usar conditional_edge para decidir el siguiente nodo
workflow_topics.add_conditional_edges(
    START,  # Nodo de inicio
    conditional_routing,  # Función que decide el siguiente nodo
    {
        "initialize": "initialize",  # Si la función retorna "initialize", va al nodo "initialize"
        "chatbot": "chatbot",  # Si la función retorna "chatbot", va al nodo "chatbot"
    }
)

# Terminar flujo después de cada nodo
workflow_topics.add_edge("initialize", END)
workflow_topics.add_edge("chatbot", END)

# Compilar el agente
topics_agent = workflow_topics.compile()
topics_agent.name = "Topics Generation"
