# AI Agents for supported employment job coaches

This project implements intelligent AI agents designed to generate educational content for employee onboarding and training. Built with Microsoft Azure services and advanced AI models, the system streamlines the learning experience for new employees.

## 🧠 Project Overview

The solution employs specialized AI agents to:

* ✅ Generate multiple-choice questions for knowledge assessment
* 📚 Coach employees on various topics
* 📂 Generate and classify relevant topics for training
* 🔄 Collect and analyze user feedback for continuous improvement

## 🛠️ Technologies Used

* 🔧 **LangGraph**: For constructing and managing AI agent workflows
* 🔍 **Azure AI Search**: To store and retrieve embeddings for topic analysis
* 🤖 **Azure OpenAI**: For natural language processing and question generation
* 🐍 **FastAPI**: Backend framework for API development
* ☁️ **Azure App Services**: For deploying and scaling the FastAPI application
* 💾 **Cosmos DB**: For storing user feedback and interactions

## 📁 Project Structure

* 🧠 **Agents**: AI agents for topic generation, coaching, and feedback
* 🔧 **FastAPI Backend**: Manages API endpoints for interacting with AI agents
* 🔍 **Azure AI Search**: Embeddings for fast and accurate topic retrieval
* 💾 **Cosmos DB**: Stores feedback and learning analytics

## 🚀 Installation

### 1. Setting up Development Environment

Create a virtual environment to isolate project dependencies:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 2. Installing Poetry

Install Poetry for dependency management:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version
```

### 3. Installing Dependencies

Use Poetry to install all project dependencies:

```bash
# Install dependencies
poetry install
```

### 4. Running the Agents

To run and develop the LangGraph agents:

```bash
# Start the LangGraph development server
langgraph dev
```

### 5. Running the API Endpoints

Start the FastAPI application:

```bash
# Start the FastAPI development server
fastapi dev src/react_agent/api.py
```

Access the API documentation at `http://localhost:8000/docs`

## 🌐 Environment Variables

Set the following environment variables to ensure proper configuration:

### [Azure OpenAI Configuration](https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/OpenAI)
* `AZURE_OPENAI_API_KEY`
* `AZURE_OPENAI_ENDPOINT`
* `AZURE_DEPLOYMENT_NAME=gpt-35-turbo-deployment`
* `AZURE_OPENAI_API_VERSION` - [API Reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)

### [Azure Cosmos DB Configuration](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.DocumentDB%2FdatabaseAccounts)
* `COSMOS_ENDPOINT`
* `COSMOS_KEY`
* `COSMOS_DATABASE_NAME`
* `COSMOS_CONTAINER_NAME`

### [Langsmith Configuration](https://www.langsmith.com/dashboard)
* `LANGSMITH_PROJECT`
* `LANGSMITH_API_KEY` - [API Keys](https://www.langsmith.com/dashboard/settings/api-keys)

### [Azure Search Configuration](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.Search%2FsearchServices)
* `VECTOR_STORE_ADDRESS`
* `VECTOR_STORE_PASSWORD`
* `VECTOR_STORE_INDEX_NAME`

### [Azure Text Embedding Configuration](https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/OpenAI)
* `AZURE_TEXT_EMBEDDING_ENDPOINT`
* `AZURE_TEXT_EMBEDDING_API_KEY`
* `AZURE_TEXT_EMBEDDING_API_VERSION` - [API Reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)
* `AZURE_TEXT_EMBEDDING_DEPLOYMENT=text-embedding-3-large`

## 🚀 Azure Deployment

Follow these steps to deploy the application to Azure:

### 1. Login to Azure CLI

```bash
az login
```

### 2. Ensure Azure CLI is up to date

```bash
az upgrade
```

### 3. Create a Resource Group

```bash
az group create --name web-app-simple-rg --location eastus
```

### 4. Create Azure Container Registry

Replace `<container-registry-name>` with your unique registry name.

```bash
az acr create --resource-group web-app-simple-rg \
--name <container-registry-name> --sku Basic
```

### 5. Build and Push Docker Image

```bash
az acr build \
  --resource-group web-app-simple-rg \
  --registry <container-registry-name> \
  --image webappsimple:latest .
```

### 6. Create App Service Plan

```bash
az appservice plan create \
--name webplan \
--resource-group web-app-simple-rg \
--sku B1 \
--is-linux
```

### 7. Deploy to Azure Web App

```bash
SUBSCRIPTION_ID=$(az account show --query id --output tsv)
az webapp create \
--resource-group web-app-simple-rg \
--plan webplan --name <container-registry-name> \
--assign-identity [system] \
--role AcrPull \
--scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/web-app-simple-rg \
--acr-use-identity --acr-identity [system] \
--container-image-name <container-registry-name>.azurecr.io/webappsimple:latest 
```

### 8. Configure Environment Variables

After deployment, set all the required environment variables in the Azure Web App Configuration section in the Azure Portal or use the following Azure CLI command:

```bash
az webapp config appsettings set --resource-group web-app-simple-rg --name <container-registry-name> --settings AZURE_OPENAI_API_KEY=<value> AZURE_OPENAI_ENDPOINT=<value> ...
```
