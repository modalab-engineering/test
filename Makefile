install:
	uv pip sync requirements.txt

install-dev:
	uv pip sync requirements-dev.txt

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
