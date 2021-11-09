
test: typecheck test-e2e ## Execute all tests
.PHONY: test

typecheck:
	. ${PWD}/venv/bin/activate
	find . \( -path ./venv -o -path ./build \) -prune -false -o -iname "*.py" -type f -exec mypy {} \;
.PHONY: typecheck


test-e2e: ## Execute all E2E tests
	python3 main.py --input ./data/test1.mm --formatter print_as_titles.py > data/test1.actual
	diff -q data/test1.actual data/test1.expected
.PHONY: test-e2e