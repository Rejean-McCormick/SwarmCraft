import json
from jsonschema import validate

# Simple skeleton for config loader. In real code, this would load from disk and validate.

SCHEMA = {
    "type": "object",
    "properties": {
        "source": {"type": "string"},
        "destination": {"type": "string"}
    },
    "required": ["source", "destination"]
}


def load_config(config_path: str):
    with open(config_path, 'r') as f:
        cfg = json.load(f)
    validate(instance=cfg, schema=SCHEMA)
    return cfg
