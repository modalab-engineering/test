FROM python:3.13-slim

# Instala dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    libpq-dev \
    bash \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /program

# Copia el archivo de requerimientos
COPY requirements.txt .
COPY requirements-dev.txt .

# Actualiza pip e instala las dependencias globalmente sin cache
RUN pip install --upgrade pip uv && \
    uv pip install --system --no-cache -r requirements.txt && \
    uv pip install --system --no-cache -r requirements-dev.txt


ENV PYTHONPATH="${PYTHONPATH}:${PWD}"


# Copia el resto del código de la aplicación
COPY . .
# COPY helpers/download_model.py .
RUN python helpers/download_model.py


ENV TRANSFORMERS_CACHE="/program/model_cache"
# Expone el puerto 8080 para la aplicación
EXPOSE 8080
# Comando de inicio, uvicorn se instalará en el PATH global
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
