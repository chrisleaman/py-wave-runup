install:
	poetry install

docs:
	poetry run sphinx-build -M html ".\docs" ".\docs\_build"

docs-requirements.txt:
	poetry run pip freeze --exclude-editable > ./docs/requirements.txt
