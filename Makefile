include makefiles/docker-compose.mk
include makefiles/virtualenvironment.mk

install: requirements install-githooks
.PHONY: install

install-githooks: check-virtual-env
	pre-commit install
.PHONY: install-githooks

test: check-virtual-env typecheck test-python ## Execute all tests
.PHONY: test

test-python: check-virtual-env
	pytest .
.PHONY: test-python
