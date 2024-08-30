import json
from typing import Any


def prepare_schemas(models: list[Any]) -> str:
    """Prepare the JSON schemas for a list of pydantic models.

    Args:
        models (list[Any]): A list of pydantic model instances.

    Returns:
        str: A string containing the JSON schemas for the models.
    """
    schemas: list = [model().model_json_schema() for model in models]
    for schema in schemas:
        del schema["title"]
    return "\n".join([f"```json\n{json.dumps(schema, indent=4)}\n```" for schema in schemas])
