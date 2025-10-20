# GCP Debug Agent

A diagnostic agent designed to explore and document the GCP environment, permissions, and resources available during CI/CD workflow execution.

## Purpose

This agent helps developers understand:
- What GCP service account is being used
- What permissions and roles are available
- What GCP resources can be accessed (buckets, secrets, etc.)
- What environment variables are set during workflow execution
- What Vertex AI capabilities are available
- GitHub Actions context information

## Features

The debug agent provides the following introspection capabilities:

### Identity & Authentication
- **get_current_identity()**: Shows the service account email and project ID
- **test_common_permissions()**: Tests access to common GCP services

### GCP Resources
- **list_storage_buckets()**: Lists accessible GCS buckets
- **list_secrets()**: Lists available Secret Manager secrets
- **get_project_info()**: Shows detailed project information
- **list_vertex_ai_models()**: Shows Vertex AI configuration

### Environment
- **list_environment_variables()**: Lists all environment variables (sensitive values redacted)
- **get_github_context()**: Shows GitHub Actions workflow context

## Usage

### In CI/CD Workflow

When you open a PR with changes to this agent, the GitHub Actions workflow will:

1. Generate a test agent from this template
2. Install dependencies with `make install`
3. Run the integration tests with `make test`
4. The tests will dump comprehensive environment information to the logs

### Viewing Results

After the workflow runs, check the GitHub Actions logs for the test output. The integration tests will print detailed information about:

- Current service account and project
- Available GCP resources
- Permissions and access levels
- Environment configuration
- GitHub Actions context

Look for sections marked with `===` banners in the test output.

## Test Structure

The agent includes comprehensive integration tests in `tests/test_agent.py`:

- `test_debug_agent_stream()`: Tests the agent's conversational interface
- `test_get_current_identity()`: Dumps identity information
- `test_list_environment_variables()`: Shows environment variables
- `test_list_storage_buckets()`: Lists accessible buckets
- `test_list_secrets()`: Lists Secret Manager secrets
- `test_get_project_info()`: Shows project details
- `test_list_vertex_ai_models()`: Shows Vertex AI configuration
- `test_get_github_context()`: Shows GitHub Actions context
- `test_common_permissions()`: Tests common permissions
- `test_comprehensive_dump()`: Runs all diagnostics in sequence

## What You'll Learn

By running this agent in the CI/CD workflow, you'll discover:

1. **Service Account**: The exact service account email and type used during testing
2. **Project**: The GCP project ID where agents are deployed (e.g., `adk-devops`)
3. **Buckets**: Which GCS buckets are accessible, including:
   - `adk-devops-agent-engine` (for Agent Engine deployments)
   - `adk-devops-test-*-logs` (for agent logs)
4. **Secrets**: What secrets are available in Secret Manager
5. **Permissions**: What operations are allowed (list buckets, access secrets, deploy to Vertex AI, etc.)
6. **Environment**: What environment variables are set, including:
   - GitHub Actions variables (GITHUB_WORKFLOW, GITHUB_ACTOR, etc.)
   - GCP variables (GOOGLE_CLOUD_PROJECT, etc.)
7. **Vertex AI**: Which regions and models are available

## Agent Configuration

The agent is configured in `pyproject.toml` with:

```toml
[tool.agent-starter-pack.settings]
agent_directory = "gcp_debug_agent"
deployment_targets = ["agent_engine"]
```

This means the agent will be tested with the `agent_engine` deployment target, which uses Vertex AI Agent Engine.

## Example Output

When the tests run, you'll see output like:

```
================================================================================
CURRENT IDENTITY INFORMATION
================================================================================
{
  "project_id": "adk-devops",
  "credentials_type": "Credentials",
  "service_account_email": "github-actions@adk-devops.iam.gserviceaccount.com"
}
================================================================================

================================================================================
PERMISSION TESTS
================================================================================
{
  "storage": "Can list buckets",
  "secret_manager": "Can list secrets",
  "vertex_ai": "Can initialize Vertex AI",
  "resource_manager": "Can get project info"
}
================================================================================
```

## Contributing

This is a diagnostic tool. Feel free to add more introspection functions to explore additional GCP resources or capabilities.

## License

Apache-2.0
