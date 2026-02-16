"""
Services module for external integrations.

Provides unified interfaces for:
- Dapr service invocation
- Event publishing
- State management
"""

from services.dapr_client import DaprClient, get_dapr_client, HttpMethod

__all__ = ["DaprClient", "get_dapr_client", "HttpMethod"]
