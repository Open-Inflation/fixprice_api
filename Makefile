.PHONY: help install install-dev test test-quick lint format type-check clean build docs example-docs build-all-docs serve-docs serve-examples ci-test prepare-release generate-badges

install:
	pip install .

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest --cov=fixprice_api --cov-report=xml --cov-report=html --cov-report=term-missing

test-quick:
	pytest --tb=short

lint:
	python -m ruff check fixprice_api tests example.py docs/source/conf.py

type-check:
	python -m mypy fixprice_api

format:
	python -m ruff check --select I --fix fixprice_api tests example.py docs/source/conf.py
	python -m ruff format fixprice_api tests example.py docs/source/conf.py

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf docs/_build/ examples/docs/_build/
	rm -rf htmlcov/ .coverage coverage.xml coverage.svg
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

build-install:
	$(MAKE) build
	$(MAKE) install

docs:
	cd docs && sphinx-build -b html source _build/html

serve-docs:
	cd docs/_build/html && python -m http.server 8000
