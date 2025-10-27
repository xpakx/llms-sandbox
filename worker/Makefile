.PHONY: run mypy test 

all: run

run:
	uv run -m worker.main

mypy:
	uvx mypy worker/

test:
	PYTHONPATH=../worker uvx pytest
