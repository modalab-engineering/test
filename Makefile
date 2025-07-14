install:
	uv pip install -r requirements.txt

install-dev:
	uv pip install -r requirements-dev.txt

update-deps:
	uv pip compile pyproject.toml --output-file requirements.txt
	uv pip compile pyproject.toml --extra dev --output-file requirements-dev.txt

format:
	black .
	isort .

lint:
	flake8 .

test:
	pytest --cov==src

pre-commit:
	pre-commit run --all-files

dev:
	uvicorn app.main:app --reload

# ---- Docker Image
REGION    ?= us-central1
PROJECT   ?= $(shell gcloud config get-value project)
REPOSITORY ?= search
API_NAME ?= modalab-search
IMAGE ?= $(REGION)-docker.pkg.dev/$(PROJECT)/$(REPOSITORY)/$(API_NAME):latest

# Cloud Run setup
CPU       ?= 2
MEM       ?= 4Gi
CONC      ?= 1

build:
	docker build \
		--platform linux/amd64 \
		-f Dockerfile \
        -t $(IMAGE) .

push: build
	@echo "Deploying to Cloud Run..."
	gcloud auth configure-docker $(REGION)-docker.pkg.dev
	docker push $(IMAGE)

deploy: push
	gcloud run deploy $(API_NAME) \
	  --image $(IMAGE) \
	  --region $(REGION) \
	  --platform managed \
	  --allow-unauthenticated \
	  --cpu $(CPU) --memory $(MEM) --concurrency $(CONC) \
	  --min-instances 1 \            # keep it warm
	  --no-cpu-throttling \          # keep CPU on for the worker
	  --max-instances 2 \
	  --set-env-vars PYTHONUNBUFFERED=1

run: build
	docker run --env-file .env \
		-p 8000:8000 $(IMAGE)
