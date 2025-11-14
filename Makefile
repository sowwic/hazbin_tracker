SHELL := /bin/bash
MAIN_FILE_PATH := ./src/nyx/main.py


clean:
	rm -rf .mypy_cache
	rm -rf .pytest_cache

lint:
	poetry run flake8 src tests

typecheck:
	poetry run mypy src tests

pytest:
	poetry run pytest tests

check: lint typecheck

full-check: lint typecheck pytest