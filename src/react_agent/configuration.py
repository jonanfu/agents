"""Define the configurable parameters for the agent."""

from dotenv import load_dotenv
import os

class Config:
    """Carga la configuración desde variables de entorno."""
    load_dotenv()

    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

    # Azure Cosmos DB Configuration
    COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
    COSMOS_KEY = os.getenv("COSMOS_KEY")
    COSMOS_DATABASE_NAME = os.getenv("COSMOS_DATABASE_NAME")
    COSMOS_CONTAINER_NAME = os.getenv("COSMOS_CONTAINER_NAME")

    # Azure Search Configuration
    VECTOR_STORE_ADDRESS = os.getenv("VECTOR_STORE_ADDRESS")
    VECTOR_STORE_PASSWORD = os.getenv("VECTOR_STORE_PASSWORD")

    # Azure Text Embedding Configuration
    AZURE_TEXT_EMBEDDING_ENDPOINT = os.getenv("AZURE_TEXT_EMBEDDING_ENDPOINT")
    AZURE_TEXT_EMBEDDING_API_KEY = os.getenv("AZURE_TEXT_EMBEDDING_API_KEY")
    AZURE_TEXT_EMBEDDING_API_VERSION = os.getenv("AZURE_TEXT_EMBEDDING_API_VERSION")
    AZURE_TEXT_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_TEXT_EMBEDDING_DEPLOYMENT")

