from typing import Dict

from .contracts import CORE_ENDPOINTS


def build_openapi_document() -> Dict[str, object]:
    paths: Dict[str, Dict[str, object]] = {}
    for endpoint in CORE_ENDPOINTS:
        path_doc = paths.setdefault(endpoint.path, {})
        path_doc[endpoint.method.lower()] = {
            "summary": endpoint.summary,
            "responses": {
                "200": {"description": "Success"},
                "401": {"description": "Unauthorized"},
                "403": {"description": "Forbidden"},
            },
            "x-required-permission": endpoint.permission,
        }

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Substrate Scaffold API",
            "version": "3.0.0",
            "description": "Contract-first API surface for governance modules.",
        },
        "paths": paths,
    }
