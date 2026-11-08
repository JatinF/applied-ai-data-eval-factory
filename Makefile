.PHONY: lint typecheck test run serve package regression

lint:
	ruff check src tests scripts

typecheck:
	mypy src

test:
	pytest

run:
	data-eval run

serve:
	data-eval serve --host 127.0.0.1 --port 8000

package:
	python -m build

regression:
	data-eval check-regression
