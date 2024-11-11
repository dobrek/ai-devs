.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a

.PHONY: polygon
polygon: ## Run "POLIGON" task
	@echo "🚀 Running POLIGON task"
	@uv run --directory ai_dev3 polygon.py

.PHONY: anti_captcha
anti_captcha: ## Run "ANTY-CAPTCHA" task
	@echo "🚀 Running ANTY-CAPTCHA task"
	@uv run --directory ai_dev3 anti_captcha.py

.PHONY: veryfi
veryfi: ## Run "VERYFI" task
	@echo "🚀 Running VERYFI task"
	@uv run --directory ai_dev3 veryfi.py

.PHONY: json_report
json_report: ## Run "JSON" task
	@echo "🚀 Running JSON task"
	@uv run --directory ai_dev3 json_report.py

.PHONY: censorship
censorship: ## Run "CENZURA" task
	@echo "🚀 Running CENZURA task"
	@uv run --directory ai_dev3 censorship.py

.PHONY: run
run: ## Run task with the name passed in the task variable
	@echo "🚀 Running ${task} task"
	@uv run --directory ai_dev3 ${task}.py

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
