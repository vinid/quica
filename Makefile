.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
PROJECT:=quica

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 $(PROJECT) tests

test: ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source $(PROJECT) -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/$(PROJECT).rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ $(PROJECT)
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install


# Docker image build info
BUILD_TAG?=latest

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@echo "Quica webapp"
	@echo "====================="
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

########################################################
## Local development
########################################################

build: ## Build the latest image
	docker build -t $(PROJECT):${BUILD_TAG} .

exec: DARGS?=-v $(PWD):/app
exec: ## Exec into the container
	docker run -it --rm $(DARGS) $(PROJECT) bash

dev: DARGS?=-v $(PWD):/app -p 6006:80  # NOTE docker port must be 80
dev: ## Run dev mode (do not detach terminal)
	docker run --name wordify-container -it --rm $(DARGS) $(PROJECT):${BUILD_TAG}

container: DARGS?=-v $(PWD):/app -p 6006:80  # NOTE docker port must be 80
container: ## Run wordify
	docker run -d --name wordify-container -it --rm $(DARGS) $(PROJECT):${BUILD_TAG}

deploy: ## Deployment
	git pull origin master
	docker image rm $(PROJECT):${BUILD_TAG}
    # Build the image before stopping the container 
	# (This will NOT affect the existing container using the old image)
	docker build -t $(PROJECT):${BUILD_TAG} .
	docker stop wordify-container
	docker run -d --name wordify-container -it --rm -v $(PWD):/app -p 6006:80 $(PROJECT):${BUILD_TAG}
