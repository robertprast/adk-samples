"""Unit tests for GCP Debug Agent."""

import json

from gcp_debug_agent.agent import (
    get_github_context,
    list_environment_variables,
)


def test_list_environment_variables():
    """Test that environment variables can be listed."""
    result = list_environment_variables()
    data = json.loads(result)
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_github_context():
    """Test that GitHub context can be retrieved."""
    result = get_github_context()
    data = json.loads(result)
    assert isinstance(data, dict)


def test_environment_variable_redaction():
    """Test that sensitive environment variables are redacted."""
    result = list_environment_variables()
    data = json.loads(result)
    
    # Check that any variable with sensitive keywords is redacted
    sensitive_keywords = ["TOKEN", "SECRET", "PASSWORD", "KEY", "CREDENTIAL"]
    for key, value in data.items():
        if any(keyword in key.upper() for keyword in sensitive_keywords):
            assert value == "***REDACTED***" or "***REDACTED***" in str(value)
