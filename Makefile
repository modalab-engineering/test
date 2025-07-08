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

build-docker:
	docker build \
		-f Dockerfile \
        -t modalab_search .

run-docker: build-docker
	docker run --env-file .env \
		-p 8000:8000 modalab_search
