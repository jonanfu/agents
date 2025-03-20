"""Utility & helper functions."""
import uuid
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from react_agent.prompts import QUESTION_PROMPT, TOPICS_GET_PROMPT, GENERATE_JSON_TOPICS_PROMPT
from langchain.chains import LLMChain
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from react_agent.state import QuestionState
from azure.cosmos import CosmosClient
from typing import List, Dict, Any, Literal
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

from react_agent.configuration import Config
import json
import logging
import re


config = Config()

def load_model() -> AzureChatOpenAI:
    """Load and configure the Azure OpenAI model."""
    return AzureChatOpenAI(
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
        azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
        api_version=Config.AZURE_OPENAI_API_VERSION,
        api_key=Config.AZURE_OPENAI_API_KEY,
        temperature=0.7,
    )


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


def load_text_embedding_model() -> AzureOpenAIEmbeddings:
    return AzureOpenAIEmbeddings(
        azure_endpoint=config.AZURE_TEXT_EMBEDDING_ENDPOINT,
        azure_deployment=config.AZURE_TEXT_EMBEDDING_DEPLOYMENT,
        api_version=config.AZURE_TEXT_EMBEDDING_API_VERSION,
        api_key=config.AZURE_TEXT_EMBEDDING_API_KEY,
    )


def load_vector_store(index_name: str, embeddings: AzureOpenAIEmbeddings) -> AzureSearch:
    return AzureSearch(
        azure_search_endpoint=config.VECTOR_STORE_ADDRESS,
        azure_search_key=config.VECTOR_STORE_PASSWORD,
        index_name=index_name,
        embedding_function=embeddings.embed_query
    )


def clean_text(text: str) -> str:
    """Limpia el texto eliminando espacios extra y caracteres especiales innecesarios."""
    text = re.sub(r'\s+', ' ', text)  # Reemplaza múltiples espacios con uno solo
    text = text.strip()  # Elimina espacios al inicio y final
    return text

def save_embeddings(index_name: str, pdf_path: str):
    """Guarda los embeddings en Azure Search."""

    embeddings = load_text_embedding_model()
    vector_store = load_vector_store(index_name, embeddings)
    loader = PyPDFLoader(pdf_path)

    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    vector_store.add_documents(documents=docs)

    

def generate_topics(index_name: str) -> List[str]:
    """Genera topics para el índice de Azure Search."""
    model = load_model()
    
    index_client = SearchIndexClient(endpoint=config.VECTOR_STORE_ADDRESS,
                                credential=AzureKeyCredential(config.VECTOR_STORE_PASSWORD))

    result = index_client.get_search_client(index_name)

    docs = result.search(search_text="*")

    prompt = PromptTemplate(
        input_variables=["content"],
        template=TOPICS_GET_PROMPT,
    )

    # Crear la cadena para procesar el texto y obtener los temas
    chain = LLMChain(llm=model, prompt=prompt)

# Generar los temas para cada fragmento del documento
    topics = []
    for doc in docs:
        content = doc["content"]
        result = chain.run(content)  # Generar los temas del contenido
        topics.append(result)
    
    return topics


def generate_json_topics(lista_topics: List[str], training_name: str, url: str) -> Dict[str, Any]:
    """Genera un JSON con los temas para el índice de Azure Search."""
    model = load_model()

    prompt = GENERATE_JSON_TOPICS_PROMPT.format(lista=lista_topics, training_name=training_name, url=url)
    response = model.invoke(prompt)    

    if not response or not response.content:
        print("No se recibió respuesta del modelo")
        return {"messages": "No se recibió respuesta del modelo"}
    else:
        result = json.loads(response.content)
        return result

def save_topics(json_topics: Dict[str, Any], container_name: str):
    """Guarda el JSON de temas en Cosmos DB."""
    client = CosmosClient(config.COSMOS_ENDPOINT, credential=config.COSMOS_KEY)
    database = client.get_database_client(config.COSMOS_DATABASE_NAME)
    container = database.create_container_if_not_exists (
        id=container_name
    )

    try:
        container.create_item(json_topics)
        return json_topics
    except Exception as e:
        logging.error(f"Error al guardar en Cosmos DB: {str(e)}")
        return json_topics








