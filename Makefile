SHELL := /bin/bash
MAIN_FILE_PATH := ./src/nyx/main.py


clean:
	rm -rf .pytest_cache

lint:
	poetry run flake8 src tests

pytest:
	poetry run pytest tests

check: lint pytest