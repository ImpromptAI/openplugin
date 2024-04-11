#!/usr/bin/make

include .env

help:
	@echo "make"
	@echo "    install"
	@echo "        Install all packages of poetry project locally."
	@echo "    start-server"
	@echo "        Start the server using uvicorn."
	@echo "    build-lambda-docker"
	@echo "        Build the Docker image for the lambda function."
	@echo "    run-lambda-docker"
	@echo "        Run the Docker image for the lambda function."
	@echo "    run-lambda-docker-bg"
	@echo "        Run the Docker image for the lambda function in the background."
	@echo "    stop-lambda-docker"
	@echo "        Stop the Docker container running the lambda function."
	@echo "    build-docker"
	@echo "        Build the Docker image for the application."
	@echo "    run-docker"
	@echo "        Run the Docker image for the application."
	@echo "    run-docker-bg"
	@echo "        Run the Docker image for the application in the background."
	@echo "    stop-docker"
	@echo "        Stop the Docker container running the application."
	@echo "    build-docs"
	@echo "        Build the documentation using Sphinx."
	@echo "    formatter"
	@echo "        Format the Python code using Black."
	@echo "    lint"
	@echo "        Lint the Python code using ruff and Black."
	@echo "    mypy"
	@echo "        Check the Python code for type errors using mypy."
	@echo "    lint-watch"
	@echo "        Watch for changes and lint the Python code using ruff."
	@echo "    lint-fix"
	@echo "        Automatically fix linting errors using ruff."
	

start-server:
	poetry run uvicorn openplugin.api.application:app --reload --host $(HOST) --port $(PORT)

build-lambda-docker:
	docker build -t openplugin-lambda -f Dockerfile.lambda .

run-lambda-docker:
	docker run -p 8003:8003 openplugin-lambda

run-lambda-docker-bg:
	docker run -p 8003:8003 -d openplugin-lambda

stop-lambda-docker:
	docker stop $(docker ps -a -q --filter ancestor=openplugin-lambda --format="{{.ID}}")

build-docker:
	docker build -t openplugin -f Dockerfile .

run-docker:
	docker run -p 8003:8003 openplugin

run-docker-bg:
	docker run -p 8003:8003 -d openplugin

stop-docker:
	docker stop $(docker ps -a -q --filter ancestor=openplugin --format="{{.ID}}")

build-docs:
	sphinx-build docs/source _build

formatter:
	poetry run black openplugin

lint:
	poetry run ruff app && poetry run black --check openplugin

mypy:
	poetry run mypy .

lint-watch:
	poetry run ruff app --watch

lint-fix:
	poetry run ruff app --fix
