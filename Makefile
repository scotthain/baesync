.PHONY: install test lint clean build

install:
	pip install -e .

test:
	pytest

lint:
	black .
	isort .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python -m build

all: install lint test 