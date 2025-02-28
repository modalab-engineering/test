FROM python:3.10-slim-buster

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get -y install gcc g++ python3-dev build-essential

# Define el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requerimientos desde la raíz del proyecto
COPY requirements.txt .

# Actualiza pip e instala las dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el directorio del front (desde la raíz, donde se encuentra la carpeta front)
COPY front /app/front

# Cambia el directorio de trabajo al del front
WORKDIR /app/front

# Expone el puerto por defecto de Streamlit (8501)
EXPOSE 8501

# Comando para iniciar la aplicación de Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
