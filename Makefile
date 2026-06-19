VENV = .env
PY = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
FLAKE = $(VENV)/bin/flake8
MYPY = $(VENV)/bin/mypy 
MARKER=$(VENV)/.installed 



clean:
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@echo "Cleaning all project cache files..."
# 1. Finds and deletes all __pycache__ folders anywhere
	@find . -type d -name "__pycache__" -exec rm -rf {} +
# 2. Deletes lingering compiled python files anywhere
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
# 3. Recursively removes Mypy and Pytest cache folders anywhere
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "Project directory is completely clean!"
	@echo "\033[92m [INFO]:\033[0m To clean the env check if [env] is not activated:"
	@echo "-> If [env] is activated: run <deactivate>"
	@echo "-> Then run <rm -rf env>"

lint:
	@echo "Running lint flake8..."
	@$(FLAKE) --exclude=$(VENV) . && echo "Flake8 is [OK]!"
	@echo "Running mypy"
	@$(MYPY) --exclude $(VENV) --exclude test.py  --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .
