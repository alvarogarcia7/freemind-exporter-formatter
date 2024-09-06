include makefiles/docker-compose.mk
include makefiles/virtualenvironment.mk

install: requirements install-githooks
.PHONY: install

install-githooks: check-virtual-env
	pre-commit install
.PHONY: install-githooks

test: check-virtual-env typecheck test-python test-e2e ## Execute all tests
.PHONY: test

test-python: check-virtual-env
	echo pytest . - NO OP
.PHONY: test-python

test-e2e: test-e2e-print_as_titles test-e2e-leaf_as_text ## Execute all E2E tests
.PHONY: test-e2e

test-e2e-leaf_as_text:
	rm -f ./data/*actual
	python3 main.py --input ./data/test1.mm --formatter leaf_as_text.py > data/test1_leaf_as_text.actual
	diff -q data/test1_leaf_as_text.actual data/test1_leaf_as_text.expected
.PHONY: test-e2e-leaf_as_text

test-e2e-print_as_titles:
	rm -f ./data/*actual
	python3 main.py --input ./data/test1.mm --formatter print_as_titles.py > data/test1_print_as_titles.actual
	diff -q data/test1_print_as_titles.actual data/test1_print_as_titles.expected
.PHONY: test-e2e-print_as_titles

pre-commit: test ## Git hook for pre-commit
.PHONY: pre-commit