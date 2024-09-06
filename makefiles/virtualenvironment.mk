# This Makefile has been designed to be executed from the top folder, not from the makefiles folder.
# Hence why the include includes the `makefiles` folder.
include makefiles/python_version.mk

virtualenvironment:
	$(PYTHON) -m venv venv
.PHONY: virtualenvironment

virtualenvironment-finish: check-virtual-env
	$(PYTHON) -m ensurepip --upgrade
	$(PIP) install --upgrade setuptools
.PHONY: virtualenvironment-finish

check-virtual-env:
	@# Test if the variable is set
	@if [ -z "${VIRTUAL_ENV}" ]; then                                               \
  		echo "Need to activate virtual environment: source ./venv/bin/activate";    \
  		false;       																\
  	fi

requirements.txt: check-virtual-env
	pip3 freeze > requirements.txt
.PHONY: requirements.txt

freeze: requirements.txt

typecheck: check-virtual-env
	mypy . --exclude venv
.PHONY: typecheck

requirements: check-virtual-env
	pip3 install -r requirements.txt
