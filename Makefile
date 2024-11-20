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

.PHONY: run
run: ## Run task with the name passed in the task variable
	@echo "🚀 Running ${task} task"
	@uv run ${task}

.PHONY: qdrant
qdrant: ## Run qdrant - vector search engine
	@echo "🚀 Running ${task} task"
	@docker run -p 6333:6333 -p 6334:6334 -d --name qdrant-ai-devs -v ./data/qdrant_storage:/qdrant/storage:z qdrant/qdrant


.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
