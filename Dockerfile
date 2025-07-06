FROM python:3.12-alpine

# Instala dependencias del sistema necesarias para compilar paquetes Python
RUN apk add --no-cache gcc musl-dev postgresql-dev bash curl jq

WORKDIR /program

# Copia el archivo de requerimientos
COPY requirements.txt .

# Actualiza pip e instala las dependencias globalmente sin cache
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto 8080 para la aplicación
EXPOSE 8080

# Comando de inicio, uvicorn se instalará en el PATH global
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
