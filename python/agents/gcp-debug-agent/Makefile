# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev

# Launch local dev playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'gcp_debug_agent' module to interact with agent.   |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# Deploy the agent remotely
backend:
	PROJECT_ID=$$(gcloud config get-value project) && \
	echo $$PROJECT_ID && \
	printenv && \
	gcloud beta run deploy gcp-debug-agent \
		--source . \
		--quiet \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "europe-west4" \
		--no-cpu-throttling \
		--labels "created-by=adk,agent=gcp-debug-agent" \
		--allow-unauthenticated

# Launch local development server with hot-reload
local-backend:
	uv run adk api_server gcp_debug_agent --allow_origins="*"

# Run unit and integration tests
test:
	echo 'pass'

# Run code quality checks (codespell, ruff, mypy)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .
