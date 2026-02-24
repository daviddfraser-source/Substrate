"""API contracts and server wiring for Substrate scaffold."""

from .contracts import CORE_ENDPOINTS, EndpointContract
from .openapi import build_openapi_document

__all__ = ["CORE_ENDPOINTS", "EndpointContract", "build_openapi_document"]
