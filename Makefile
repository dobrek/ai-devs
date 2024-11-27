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
	@echo "🚀 Running qdrant instance"
	@docker run -p 6333:6333 -p 6334:6334 -d --name aidevs3-qdrant -v ./data/qdrant_storage:/qdrant/storage:z qdrant/qdrant

.PHONY: neo4j
neo4j: ## Run noe4j - graph database
	@echo "🚀 Running neo4j instance"
	docker run -p 7474:7474 -p7687:7687 -d --name aidevs3-neo4j -v ./data/neo4j:/data neo4j

.PHONY: fine-tuning
fine-tuning: ## Prepare the data for fine-tuning
	@echo "🚀 Running fine-tuning data preparation"
	uv run --directory src/ai_dev3/S04E02/ fine_tuning_data.py


.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
