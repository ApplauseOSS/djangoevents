PYTHON ?= python3

export VIRTUAL_ENV := $(realpath .)/venv
export PATH := $(VIRTUAL_ENV)/bin:$(PATH)
unexport WORKON_HOME PIP_RESPECT_VIRTUALENV PIP_VIRTUALENV_BASE


# Configure THIS:
PROJECT_FOLDER=./djangoevents
PROJECT_NAME=djangoevents

help:
	@echo
	@echo 'Make targets:'
	@echo '  make install'
	@echo '    -> make install.virtualenv'
	@echo '    -> make install.runtime'
	@echo '    -> make install.package'
	@echo '  make clean'
	@echo '  make test'
	@echo '  make tdd'


# Top-level phony targets
_install__runtime = $(VIRTUAL_ENV)/bin/django-admin.py
_install__virtualenv = $(VIRTUAL_ENV)/bin/pip
_install__package = ./djangoevents.egg-info

# make should not confuse these commands with files
.PHONY: install install.virtualenv install.runtime install.package
.PHONY: clean

clean:
	rm -rf $(VIRTUAL_ENV)
	find . -type f -name '*.pyc' -print0 | xargs -0 rm -f
	find . -type d -name '__pycache__' -print0 | xargs -0 rm -rf
	rm -rf $(PROJECT_FOLDER).egg-info

# Installation
install: install.virtualenv install.runtime install.package
install.runtime:    $(_install__runtime)
install.virtualenv: $(_install__virtualenv)
install.package: $(_install__package)

$(_install__runtime):
	$(_install__virtualenv) install -r requirements.txt
	touch $@

$(_install__package):
	@echo '================================================================'
	@echo 'About to install $(PROJECT_NAME) in development mode'
	@echo 'Package would be linked within virtualenv so there is no need'
	@echo 'to reinstall it every time source code is changed'
	@echo '================================================================'
	$(VIRTUAL_ENV)/bin/python setup.py develop
	touch $@

$(_install__virtualenv):
	$(PYTHON) -mvenv $(VIRTUAL_ENV)
	@echo '================================================================'
	@echo 'You can now enable virtualenv with:'
	@echo '  source $(VIRTUAL_ENV)/bin/activate'
	@echo '================================================================'
	$(VIRTUAL_ENV)/bin/pip install -U pip
	touch $@


test:
	$(VIRTUAL_ENV)/bin/py.test ${PROJECT_FOLDER}

tdd:
	$(VIRTUAL_ENV)/bin/ptw -c -- ${PROJECT_FOLDER}

release:
    # Warning: requires setting PYPI_USERNAME and PYPI_PASSWORD environment variables
    # in order to authenticate to PyPI
	$(PYTHON) setup.py sdist release_to_pypi
