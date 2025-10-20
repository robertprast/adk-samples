"""GCP Debug Agent - Explores GCP environment and permissions during CI/CD workflow execution."""

import json
import os
from typing import Any, Dict, List

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.auth import default
from google.cloud import aiplatform, resourcemanager_v3, secretmanager, storage
from google.genai import types as genai_types


def get_current_identity() -> str:
    """Get information about the current service account and project.
    
    Returns:
        JSON string with identity information
    """
    try:
        credentials, project = default()
        
        identity_info = {
            "project_id": project,
            "credentials_type": str(type(credentials).__name__),
        }
        
        # Try to get service account email if available
        if hasattr(credentials, 'service_account_email'):
            identity_info["service_account_email"] = credentials.service_account_email
        elif hasattr(credentials, '_service_account_email'):
            identity_info["service_account_email"] = credentials._service_account_email
        
        return json.dumps(identity_info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})


def list_environment_variables() -> str:
    """List all environment variables (with sensitive values redacted).
    
    Returns:
        JSON string with environment variables
    """
    sensitive_keys = [
        "TOKEN", "SECRET", "PASSWORD", "KEY", "CREDENTIAL", 
        "AUTH", "API_KEY", "PRIVATE"
    ]
    
    env_vars = {}
    for key, value in os.environ.items():
        # Redact sensitive values
        if any(sensitive in key.upper() for sensitive in sensitive_keys):
            env_vars[key] = "***REDACTED***"
        else:
            env_vars[key] = value
    
    return json.dumps(env_vars, indent=2, sort_keys=True)


def list_storage_buckets() -> str:
    """List accessible GCS buckets.
    
    Returns:
        JSON string with bucket information
    """
    try:
        storage_client = storage.Client()
        buckets_info = []
        
        # List buckets (limit to 50)
        for i, bucket in enumerate(storage_client.list_buckets(max_results=50)):
            buckets_info.append({
                "name": bucket.name,
                "location": bucket.location,
                "storage_class": bucket.storage_class,
                "time_created": str(bucket.time_created),
            })
        
        return json.dumps({
            "bucket_count": len(buckets_info),
            "buckets": buckets_info
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})


def list_secrets() -> str:
    """List accessible secrets from Secret Manager.
    
    Returns:
        JSON string with secret names
    """
    try:
        credentials, project = default()
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project}"
        
        secrets_info = []
        for secret in client.list_secrets(request={"parent": parent}):
            secrets_info.append({
                "name": secret.name.split('/')[-1],
                "full_path": secret.name,
            })
        
        return json.dumps({
            "secret_count": len(secrets_info),
            "secrets": secrets_info
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})


def get_project_info() -> str:
    """Get information about the current GCP project.
    
    Returns:
        JSON string with project information
    """
    try:
        credentials, project_id = default()
        client = resourcemanager_v3.ProjectsClient()
        
        project_name = f"projects/{project_id}"
        project = client.get_project(name=project_name)
        
        project_info = {
            "project_id": project_id,
            "project_name": project.display_name,
            "project_number": project.name.split('/')[-1],
            "state": str(project.state),
        }
        
        return json.dumps(project_info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})


def list_vertex_ai_models() -> str:
    """List available Vertex AI models and regions.
    
    Returns:
        JSON string with model information
    """
    try:
        credentials, project = default()
        aiplatform.init(project=project, location="us-central1")
        
        # Get available regions
        regions = ["us-central1", "us-east1", "us-west1", "europe-west4"]
        
        model_info = {
            "initialized_project": project,
            "available_regions": regions,
            "note": "Vertex AI Agent Engine is available in these regions"
        }
        
        return json.dumps(model_info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})


def get_github_context() -> str:
    """Get GitHub Actions context information.
    
    Returns:
        JSON string with GitHub context
    """
    github_vars = [
        "GITHUB_WORKFLOW", "GITHUB_RUN_ID", "GITHUB_RUN_NUMBER",
        "GITHUB_ACTION", "GITHUB_ACTOR", "GITHUB_REPOSITORY",
        "GITHUB_EVENT_NAME", "GITHUB_SHA", "GITHUB_REF",
        "GITHUB_HEAD_REF", "GITHUB_BASE_REF"
    ]
    
    github_context = {}
    for var in github_vars:
        github_context[var] = os.environ.get(var, "Not set")
    
    return json.dumps(github_context, indent=2, sort_keys=True)


def test_common_permissions() -> str:
    """Test common GCP permissions to see what actions are available.
    
    Returns:
        JSON string with permission test results
    """
    permissions = {
        "storage": "Unknown",
        "secret_manager": "Unknown",
        "vertex_ai": "Unknown",
        "resource_manager": "Unknown"
    }
    
    # Test storage
    try:
        storage_client = storage.Client()
        list(storage_client.list_buckets(max_results=1))
        permissions["storage"] = "Can list buckets"
    except Exception as e:
        permissions["storage"] = f"Error: {type(e).__name__}"
    
    # Test secret manager
    try:
        credentials, project = default()
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project}"
        list(client.list_secrets(request={"parent": parent}, max_results=1))
        permissions["secret_manager"] = "Can list secrets"
    except Exception as e:
        permissions["secret_manager"] = f"Error: {type(e).__name__}"
    
    # Test Vertex AI
    try:
        credentials, project = default()
        aiplatform.init(project=project, location="us-central1")
        permissions["vertex_ai"] = "Can initialize Vertex AI"
    except Exception as e:
        permissions["vertex_ai"] = f"Error: {type(e).__name__}"
    
    # Test Resource Manager
    try:
        credentials, project_id = default()
        client = resourcemanager_v3.ProjectsClient()
        project_name = f"projects/{project_id}"
        client.get_project(name=project_name)
        permissions["resource_manager"] = "Can get project info"
    except Exception as e:
        permissions["resource_manager"] = f"Error: {type(e).__name__}"
    
    return json.dumps(permissions, indent=2)


# Create the root agent with all tools
root_agent = Agent(
    name="gcp_debug_agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are a GCP Debug Agent that helps users understand what 
    GCP resources, permissions, and environment configuration are available during CI/CD 
    workflow execution. Use your tools to inspect the environment and provide comprehensive 
    reports about the available resources.""",
    tools=[
        FunctionTool(get_current_identity),
        FunctionTool(list_environment_variables),
        FunctionTool(list_storage_buckets),
        FunctionTool(list_secrets),
        FunctionTool(get_project_info),
        FunctionTool(list_vertex_ai_models),
        FunctionTool(get_github_context),
        FunctionTool(test_common_permissions),
    ],
)


def main() -> None:
    """Main entry point for testing the agent locally."""
    print("GCP Debug Agent")
    print("=" * 60)
    
    # Test identity
    print("\n1. Current Identity:")
    print(get_current_identity())
    
    # Test environment
    print("\n2. Environment Variables (sample):")
    env = json.loads(list_environment_variables())
    print(f"Total environment variables: {len(env)}")
    for key in list(env.keys())[:5]:
        print(f"  {key}: {env[key]}")
    
    # Test permissions
    print("\n3. Permission Tests:")
    print(test_common_permissions())
    
    # Test GitHub context
    print("\n4. GitHub Context:")
    print(get_github_context())


if __name__ == "__main__":
    main()
