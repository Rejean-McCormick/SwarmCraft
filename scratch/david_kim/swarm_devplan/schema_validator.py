# Swarm Dev Plan - Schema Validator
"""JSON Schema-based payload validator for swarm contracts.

This module provides schemas for core payload types used by the AI bot swarm
and a lightweight redaction utility for sensitive fields.
"""
from __future__ import annotations

import json
from typing import Any, Dict

try:
    from jsonschema import validate as json_validate, ValidationError
except Exception:  # pragma: no cover
    # Fallback placeholder if jsonschema is not available; tests will fail gracefully
    class ValidationError(Exception):
        pass

    def json_validate(instance: Any, schema: Dict[str, Any]) -> None:
        raise ValidationError("jsonschema is not available in this environment.")

# Define JSON Schemas for core payloads
SCHEMAS: Dict[str, Dict[str, Any]] = {
    "task": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "payload_type": {"type": "string", "const": "task"},
            "payload_version": {"type": "string"},
            "task_id": {"type": "string"},
            "objective": {"type": "string"},
            "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
            "constraints": {"type": "array", "items": {"type": "string"}},
            "deadline": {"type": ["string", "null"], "format": "date-time"},
            "metadata": {"type": "object"},
            "secrets_handling": {"type": "boolean"}
        },
        "required": ["payload_type", "payload_version", "task_id", "objective", "acceptance_criteria", "constraints", "secrets_handling"]
    },
    "milestone": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "payload_type": {"type": "string", "const": "milestone"},
            "milestone_id": {"type": "string"},
            "task_id": {"type": "string"},
            "description": {"type": "string"},
            "due_date": {"type": ["string", "null"], "format": "date-time"},
            "status": {"type": "string", "enum": ["planned", "in_progress", "completed", "blocked"]},
            "assigned_to": {"type": "string"}
        },
        "required": ["payload_type", "milestone_id", "task_id", "description", "status"]
    },
    "artifact": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "payload_type": {"type": "string", "const": "artifact"},
            "artifact_id": {"type": "string"},
            "task_id": {"type": "string"},
            "artifact_type": {"type": "string"},
            "location": {"type": "string"},
            "metadata": {"type": "object"},
            "created_at": {"type": "string", "format": "date-time"}
        },
        "required": ["payload_type", "artifact_id", "task_id", "artifact_type", "location", "created_at"]
    },
    "audit": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "payload_type": {"type": "string", "const": "audit"},
            "audit_id": {"type": "string"},
            "artifact_id": {"type": "string"},
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "description": {"type": "string"},
                        "severity": {"type": "string", "enum": ["info", "low", "medium", "high", "critical"]},
                        "remediation": {"type": "string"},
                    },
                    "required": ["category", "description", "severity"]
                }
            },
            "timestamp": {"type": "string", "format": "date-time"},
            "redacted": {"type": "boolean"}
        },
        "required": ["payload_type", "audit_id", "artifact_id", "findings", "timestamp"]
    },
    "command": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "payload_type": {"type": "string", "const": "command"},
            "command_id": {"type": "string"},
            "action": {"type": "string"},
            "parameters": {"type": "object"},
            "source_bot": {"type": "string"},
            "trace_id": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"}
        },
        "required": ["payload_type", "command_id", "action", "trace_id", "timestamp"]
    }
}

REDACTION_PLACEHOLDER = "***REDACTED***"

def get_schema(payload_type: str) -> Dict[str, Any] | None:
    return SCHEMAS.get(payload_type)

def validate_payload(payload: Dict[str, Any]) -> None:
    """Validate a payload against its declared type using JSON Schema.

    The payload must include a payload_type field corresponding to one of the
    known schemas. If validation fails, a jsonschema.ValidationError is raised.
    """
    if not isinstance(payload, dict):
        raise ValidationError("payload must be a dict")
    ptype = payload.get("payload_type")
    if not ptype:
        raise ValidationError("payload_type is required in payload")
    schema = get_schema(ptype)
    if schema is None:
        raise ValidationError(f"unknown payload_type: {ptype}")
    json_validate(instance=payload, schema=schema)

def redact_payload(payload: Any, redacted_keys: list[str] | None = None) -> Any:
    """Recursively redact sensitive fields in a payload.

    redacted_keys is a list of key names (case-sensitive) to redact. If a key is
    encountered at any nesting level, its value is replaced with REDACTION_PLACEHOLDER.
    """
    if redacted_keys is None:
        redacted_keys = ["password", "secret", "token", "api_key", "access_token", "password_hash"]

    if isinstance(payload, dict):
        new_p = {}
        for k, v in payload.items():
            if k in redacted_keys:
                new_p[k] = REDACTION_PLACEHOLDER
            else:
                new_p[k] = redact_payload(v, redacted_keys)
        return new_p
    elif isinstance(payload, list):
        return [redact_payload(item, redacted_keys) for item in payload]
    else:
        return payload

# Convenience function for auditing: redact an entire audit payload safely
def redact_audit(audit_payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(audit_payload, dict):  # defensive
        return audit_payload
    return redact_payload(audit_payload)

