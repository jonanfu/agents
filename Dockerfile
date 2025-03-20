FROM python:3.11

# Instalar Poetry
RUN pip install poetry

# Crear y cambiar al directorio de la app
WORKDIR /app

# Copiar archivos
COPY . /app

# Instalar dependencias con Poetry
RUN poetry install

EXPOSE 8000

# Ejecutar la aplicación
CMD ["poetry", "run", "uvicorn", "src.react_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
