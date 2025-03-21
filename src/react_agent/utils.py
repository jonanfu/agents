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
from langchain.schema import Document   

from react_agent.configuration import Config
import json
import logging


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


def load_vector_store( embeddings: AzureOpenAIEmbeddings) -> AzureSearch:
    return AzureSearch(
        azure_search_endpoint=config.VECTOR_STORE_ADDRESS,
        azure_search_key=config.VECTOR_STORE_PASSWORD,
        index_name=config.VECTOR_STORE_INDEX_NAME,
        embedding_function=embeddings.embed_query
    )


def save_embeddings(document_id: str, pdf_path: str):
    """Guarda los embeddings en Azure Search."""  
    embeddings = load_text_embedding_model()  
    vector_store = load_vector_store(embeddings)  
    loader = PyPDFLoader(pdf_path)  
    documents = loader.load()  
  
    # Dividir el texto en fragmentos para indexarlo  
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  
    docs = text_splitter.split_documents(documents)  
  
    indexed_docs = [  
        Document(  
            page_content=doc.page_content,  # Contenido del fragmento  
            metadata={  # Agregar metadatos  
                "id": f"{document_id}_{i}",  # Genera un ID único para cada fragmento  
                "document_id": document_id,  
                "page_number": i + 1  # Número de página como metadato (opcional)  
            }  
        )  
        for i, doc in enumerate(docs)  
    ]  
  
    vector_store.add_documents(documents=indexed_docs)  
    logging.info(f"Documentos indexados con ID: {document_id}")

    
def generate_topics(document_id: str) -> List[str]:  
    """  
    Genera topics para el índice de Azure Search basado en document_id.  
    """  
    vector_store = load_vector_store(load_text_embedding_model())  
  
    # Realizar la búsqueda en el vector store  
    query = "*"  # Si deseas buscar todos los documentos relacionados  
    search_type = "similarity"  # O el tipo de búsqueda que necesitas (ajusta según tu caso)  
  
    try:  
        search_results = vector_store.search(query=query, search_type=search_type, filter=f"metadata/document_id eq '{document_id}'")  
    except Exception as e:  
        logging.error(f"Error al buscar en el vector store: {e}")  
        return []  
  
    # Validar si se encontraron documentos  
    if not search_results:  
        logging.error(f"No se encontraron documentos con document_id: {document_id}")  
        return []  
  
    model = load_model()  
    prompt = PromptTemplate(  
        input_variables=["content"],  
        template=TOPICS_GET_PROMPT,  
    )  
    chain = LLMChain(llm=model, prompt=prompt)  
  
    # Generar temas para cada fragmento del documento  
    topics = []  
    for result in search_results:  
        content = result["content"]  
        result_topics = chain.run(content)  
        topics.append(result_topics)  
  
    return topics  


def generate_json_topics(lista_topics: List[str], training_name: str, description: str, url: str) -> Dict[str, Any]:
    """Genera un JSON con los temas para el índice de Azure Search."""
    model = load_model()

    prompt = GENERATE_JSON_TOPICS_PROMPT.format(lista=lista_topics, training_name=training_name, description=description, url=url)
    response = model.invoke(prompt)    

    if not response or not response.content:
        print("No se recibió respuesta del modelo")
        return {"messages": "No se recibió respuesta del modelo"}
    else:
        result = json.loads(response.content)
        return result










