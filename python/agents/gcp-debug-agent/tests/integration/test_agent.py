"""Integration tests for GCP Debug Agent that dump environment information."""

import asyncio
import json

import pytest
from gcp_debug_agent.agent import (
    get_current_identity,
    get_github_context,
    get_project_info,
    list_environment_variables,
    list_secrets,
    list_storage_buckets,
    list_vertex_ai_models,
    root_agent,
)
# Import with alias to avoid name collision with test function
from gcp_debug_agent.agent import test_common_permissions as run_permission_tests
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types


@pytest.mark.asyncio
async def test_debug_agent_stream():
    """Test the debug agent with a streaming query."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="test_user", session_id="test_session"
    )
    runner = Runner(
        agent=root_agent, app_name="app", session_service=session_service
    )

    query = "What GCP resources and permissions are available?"
    print(f"\n>>> Query: {query}")
    
    response_parts = []
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user", 
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response_parts.append(event.content.parts[0].text)
    
    response = "\n".join(response_parts)
    print(f">>> Response: {response}")
    assert len(response) > 0


def test_get_current_identity():
    """Test getting current identity information."""
    print("\n" + "=" * 80)
    print("CURRENT IDENTITY INFORMATION")
    print("=" * 80)
    result = get_current_identity()
    print(result)
    data = json.loads(result)
    assert "project_id" in data or "error" in data
    print("=" * 80 + "\n")


def test_list_environment_variables():
    """Test listing environment variables."""
    print("\n" + "=" * 80)
    print("ENVIRONMENT VARIABLES")
    print("=" * 80)
    result = list_environment_variables()
    data = json.loads(result)
    print(f"Total environment variables: {len(data)}")
    
    # Print interesting variables
    interesting_vars = [
        "GITHUB_WORKFLOW", "GITHUB_REPOSITORY", "GOOGLE_CLOUD_PROJECT",
        "CLOUDSDK_CORE_PROJECT", "GCP_PROJECT", "GITHUB_ACTOR"
    ]
    
    for var in interesting_vars:
        if var in data:
            print(f"{var}: {data[var]}")
    
    assert len(data) > 0
    print("=" * 80 + "\n")


def test_list_storage_buckets():
    """Test listing GCS buckets."""
    print("\n" + "=" * 80)
    print("GCS BUCKETS")
    print("=" * 80)
    result = list_storage_buckets()
    print(result)
    data = json.loads(result)
    
    if "error" not in data:
        print(f"\nFound {data.get('bucket_count', 0)} buckets")
    
    print("=" * 80 + "\n")


def test_list_secrets():
    """Test listing secrets from Secret Manager."""
    print("\n" + "=" * 80)
    print("SECRET MANAGER SECRETS")
    print("=" * 80)
    result = list_secrets()
    print(result)
    data = json.loads(result)
    
    if "error" not in data:
        print(f"\nFound {data.get('secret_count', 0)} secrets")
    
    print("=" * 80 + "\n")


def test_get_project_info():
    """Test getting project information."""
    print("\n" + "=" * 80)
    print("GCP PROJECT INFORMATION")
    print("=" * 80)
    result = get_project_info()
    print(result)
    data = json.loads(result)
    assert "project_id" in data or "error" in data
    print("=" * 80 + "\n")


def test_list_vertex_ai_models():
    """Test listing Vertex AI models."""
    print("\n" + "=" * 80)
    print("VERTEX AI INFORMATION")
    print("=" * 80)
    result = list_vertex_ai_models()
    print(result)
    data = json.loads(result)
    assert "initialized_project" in data or "error" in data
    print("=" * 80 + "\n")


def test_get_github_context():
    """Test getting GitHub Actions context."""
    print("\n" + "=" * 80)
    print("GITHUB ACTIONS CONTEXT")
    print("=" * 80)
    result = get_github_context()
    print(result)
    data = json.loads(result)
    assert isinstance(data, dict)
    print("=" * 80 + "\n")


def test_common_permissions():
    """Test common GCP permissions."""
    print("\n" + "=" * 80)
    print("PERMISSION TESTS")
    print("=" * 80)
    result = run_permission_tests()
    print(result)
    data = json.loads(result)
    
    print("\nPermission Summary:")
    for service, status in data.items():
        print(f"  {service}: {status}")
    
    assert isinstance(data, dict)
    print("=" * 80 + "\n")


def test_comprehensive_dump():
    """Run all diagnostic functions and dump complete environment info."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE GCP ENVIRONMENT DUMP")
    print("=" * 80)
    
    print("\n[1/8] Current Identity")
    print("-" * 40)
    print(get_current_identity())
    
    print("\n[2/8] Project Information")
    print("-" * 40)
    print(get_project_info())
    
    print("\n[3/8] GitHub Context")
    print("-" * 40)
    print(get_github_context())
    
    print("\n[4/8] Permission Tests")
    print("-" * 40)
    print(run_permission_tests())
    
    print("\n[5/8] Storage Buckets")
    print("-" * 40)
    print(list_storage_buckets())
    
    print("\n[6/8] Secret Manager Secrets")
    print("-" * 40)
    print(list_secrets())
    
    print("\n[7/8] Vertex AI Information")
    print("-" * 40)
    print(list_vertex_ai_models())
    
    print("\n[8/8] Environment Variables (sample)")
    print("-" * 40)
    env = json.loads(list_environment_variables())
    print(f"Total variables: {len(env)}")
    print("Sample of first 10 variables:")
    for i, (key, value) in enumerate(sorted(env.items())[:10]):
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("END OF COMPREHENSIVE DUMP")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Run comprehensive dump when executed directly
    test_comprehensive_dump()
