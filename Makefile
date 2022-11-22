test: tests
tests:
	pytest


cov: coverage
coverage:
	coverage run -m pytest && coverage report -m


d_b: docker_build
docker_build:
	docker-compose build app


d_up: docker_up
docker_up:
	docker-compose up

isort:
	isort backend

fmt: format
format: isort black

black:
	black -S -l 120 backend

flake:
	flake8 --config .flake8 backend


run_api: run
run:
	source chat_fastapi_venv/bin/activate && uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000