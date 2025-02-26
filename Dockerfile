FROM python:3.10-slim-buster

RUN apt-get update && apt-get -y install gcc g++ python3-dev build-essential python3-pip

WORKDIR /program

COPY requirements.txt requirements.txt

RUN pip install uv
RUN uv venv
RUN uv pip install -r requirements.txt

# Agrega el entorno virtual al PATH
ENV PATH="/program/.venv/bin:$PATH"
ENV PYTHONPATH "${PYTHONPATH}:${PWD}"

COPY . .

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
