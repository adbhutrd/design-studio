# Open Design Studio — developer shortcuts.
# Run `make` to see the targets.

SHELL := /bin/bash
VENV  := .venv
PY    := $(VENV)/bin/python
PIP   := $(VENV)/bin/pip

.PHONY: help setup up down restart status logs test lint clean

help:
	@echo "make setup     create .venv, install runtime + dev dependencies"
	@echo "make up        start cleanup-service + gateway + app"
	@echo "make down      stop the stack"
	@echo "make status    show health of all three services"
	@echo "make logs      tail all service logs"
	@echo "make test      run the offline test suite"
	@echo "make lint      run ruff (pyflakes rules)"
	@echo "make clean     remove caches and generated output"

setup:
	bash setup.sh
	$(PIP) install --quiet -r requirements-dev.txt

up:
	bash start-all.sh

down:
	bash start-all.sh stop

restart:
	bash start-all.sh restart

status:
	bash start-all.sh status

logs:
	tail -n 40 logs/cleanup.log logs/gateway.log logs/app.log

test:
	$(PY) -m pytest -q

lint:
	$(VENV)/bin/ruff check .

clean:
	rm -rf .pytest_cache .ruff_cache app/outputs/* __pycache__ app/__pycache__
	find . -path ./.venv -prune -o -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
