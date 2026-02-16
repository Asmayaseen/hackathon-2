"""
Dapr Service Invocation Client

This module provides a unified interface for service-to-service communication
using Dapr's service invocation building block.

Benefits over direct HTTP:
- Automatic service discovery (no hardcoded URLs)
- Built-in retries and circuit breakers
- mTLS encryption between services
- Load balancing across replicas
- Distributed tracing integration

Usage:
    from services.dapr_client import DaprClient

    dapr = DaprClient()

    # Invoke another service
    response = await dapr.invoke_service(
        app_id="notification-service",
        method="api/notify",
        data={"user_id": "123", "message": "Hello"}
    )
"""

import os
import json
import logging
from typing import Any, Dict, Optional
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class HttpMethod(str, Enum):
    """HTTP methods supported by Dapr service invocation."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class DaprClient:
    """
    Dapr Service Invocation Client.

    Provides methods to invoke other services via Dapr sidecar,
    with automatic fallback to direct HTTP for local development.
    """

    def __init__(self):
        """Initialize Dapr client with sidecar configuration."""
        # Dapr sidecar HTTP port (default: 3500)
        self.dapr_http_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))

        # Dapr sidecar gRPC port (default: 50001)
        self.dapr_grpc_port = int(os.getenv("DAPR_GRPC_PORT", "50001"))

        # Base URL for Dapr sidecar
        self.dapr_base_url = f"http://localhost:{self.dapr_http_port}"

        # Check if running with Dapr
        self.dapr_enabled = os.getenv("DAPR_ENABLED", "true").lower() == "true"

        # Fallback URLs for direct service calls (local dev without Dapr)
        self.fallback_urls = {
            "notification-service": os.getenv(
                "NOTIFICATION_SERVICE_URL",
                "http://notification-service:8001"
            ),
            "todo-backend": os.getenv(
                "BACKEND_URL",
                "http://todo-backend:8000"
            ),
            "todo-frontend": os.getenv(
                "FRONTEND_URL",
                "http://todo-frontend:3000"
            ),
        }

        # HTTP client with connection pooling
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20
                )
            )
        return self._client

    async def close(self):
        """Close HTTP client connection pool."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def invoke_service(
        self,
        app_id: str,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        http_method: HttpMethod = HttpMethod.POST,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Invoke a method on another service via Dapr service invocation.

        Args:
            app_id: Target service's Dapr app ID
            method: API method/endpoint to call (without leading /)
            data: Request payload (JSON-serializable)
            http_method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            headers: Additional headers to include

        Returns:
            Response data as dictionary

        Raises:
            httpx.HTTPStatusError: On HTTP error responses
            httpx.RequestError: On connection/timeout errors

        Example:
            # Call notification service to send a reminder
            response = await dapr.invoke_service(
                app_id="notification-service",
                method="api/notify",
                data={
                    "user_id": "user123",
                    "title": "Task Reminder",
                    "message": "Your task is due soon"
                }
            )
        """
        client = await self.get_client()

        # Build headers
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if headers:
            request_headers.update(headers)

        # Choose invocation method based on Dapr availability
        if self.dapr_enabled:
            url = self._build_dapr_invoke_url(app_id, method)
            logger.debug(
                "Invoking service via Dapr: %s -> %s/%s",
                app_id, method, http_method.value
            )
        else:
            url = self._build_direct_url(app_id, method)
            logger.debug(
                "Invoking service directly (Dapr disabled): %s",
                url
            )

        try:
            # Make the request
            response = await client.request(
                method=http_method.value,
                url=url,
                headers=request_headers,
                json=data if data else None
            )

            # Raise on error status codes
            response.raise_for_status()

            # Parse response
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}

        except httpx.HTTPStatusError as e:
            logger.error(
                "Service invocation failed: %s %s -> %d %s",
                http_method.value, url,
                e.response.status_code, e.response.text
            )
            raise

        except httpx.RequestError as e:
            logger.error(
                "Service invocation connection error: %s %s -> %s",
                http_method.value, url, str(e)
            )
            raise

    def _build_dapr_invoke_url(self, app_id: str, method: str) -> str:
        """
        Build Dapr service invocation URL.

        Format: http://localhost:<dapr-port>/v1.0/invoke/<app-id>/method/<method>
        """
        # Remove leading slash if present
        method = method.lstrip("/")
        return f"{self.dapr_base_url}/v1.0/invoke/{app_id}/method/{method}"

    def _build_direct_url(self, app_id: str, method: str) -> str:
        """
        Build direct service URL for non-Dapr environments.
        """
        method = method.lstrip("/")
        base_url = self.fallback_urls.get(app_id, f"http://{app_id}:8000")
        return f"{base_url}/{method}"

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish an event to a Dapr pub/sub topic.

        Args:
            pubsub_name: Name of the pub/sub component
            topic: Topic name to publish to
            data: Event data (JSON-serializable)
            metadata: Optional metadata for the event

        Returns:
            True if published successfully

        Example:
            await dapr.publish_event(
                pubsub_name="kafka-pubsub",
                topic="task-events",
                data={"event_type": "created", "task_id": 123}
            )
        """
        if not self.dapr_enabled:
            logger.warning("Dapr disabled, skipping pub/sub publish")
            return False

        client = await self.get_client()
        url = f"{self.dapr_base_url}/v1.0/publish/{pubsub_name}/{topic}"

        headers = {"Content-Type": "application/json"}
        if metadata:
            # Dapr metadata headers have format: metadata.key
            for key, value in metadata.items():
                headers[f"metadata.{key}"] = value

        try:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            logger.info("Published event to %s/%s", pubsub_name, topic)
            return True

        except Exception as e:
            logger.error("Failed to publish event: %s", str(e))
            return False

    async def get_state(
        self,
        store_name: str,
        key: str
    ) -> Optional[Any]:
        """
        Get state from Dapr state store.

        Args:
            store_name: Name of the state store component
            key: State key to retrieve

        Returns:
            State value or None if not found
        """
        if not self.dapr_enabled:
            logger.warning("Dapr disabled, cannot get state")
            return None

        client = await self.get_client()
        url = f"{self.dapr_base_url}/v1.0/state/{store_name}/{key}"

        try:
            response = await client.get(url)
            if response.status_code == 204:
                return None
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error("Failed to get state: %s", str(e))
            return None

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        etag: Optional[str] = None
    ) -> bool:
        """
        Save state to Dapr state store.

        Args:
            store_name: Name of the state store component
            key: State key
            value: State value (JSON-serializable)
            etag: Optional ETag for concurrency control

        Returns:
            True if saved successfully
        """
        if not self.dapr_enabled:
            logger.warning("Dapr disabled, cannot save state")
            return False

        client = await self.get_client()
        url = f"{self.dapr_base_url}/v1.0/state/{store_name}"

        state_item = {
            "key": key,
            "value": value
        }
        if etag:
            state_item["etag"] = etag
            state_item["options"] = {"concurrency": "first-write"}

        try:
            response = await client.post(url, json=[state_item])
            response.raise_for_status()
            logger.info("Saved state: %s/%s", store_name, key)
            return True

        except Exception as e:
            logger.error("Failed to save state: %s", str(e))
            return False

    async def get_secret(
        self,
        store_name: str,
        key: str
    ) -> Optional[Dict[str, str]]:
        """
        Get secret from Dapr secret store.

        Args:
            store_name: Name of the secret store component
            key: Secret key to retrieve

        Returns:
            Secret value as dictionary or None
        """
        if not self.dapr_enabled:
            logger.warning("Dapr disabled, cannot get secret")
            return None

        client = await self.get_client()
        url = f"{self.dapr_base_url}/v1.0/secrets/{store_name}/{key}"

        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error("Failed to get secret: %s", str(e))
            return None


# Singleton instance for convenience
_dapr_client: Optional[DaprClient] = None


def get_dapr_client() -> DaprClient:
    """Get singleton Dapr client instance."""
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprClient()
    return _dapr_client
