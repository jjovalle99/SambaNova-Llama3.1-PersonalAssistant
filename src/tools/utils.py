import json
from typing import Any

from src.tools.schema_generation import MyGenerateJsonSchema


def lowercase_first(s: str) -> str:
    """Lowercase the first letter of a string.

    Args:
        s (str): The string to lowercase.

    Returns:
        str: The string with the first letter lowercased.
    """
    return s[0].lower() + s[1:] if s else s


def prepare_schemas(models: list[Any]) -> str:
    """Prepare the JSON schemas for a list of pydantic models.

    Args:
        models (list[Any]): A list of pydantic model instances.

    Returns:
        str: A string containing the JSON schemas for the models.
    """
    schemas: list = [model.model_json_schema(schema_generator=MyGenerateJsonSchema) for model in models]
    return "\n".join(
        [
            f"Use the function '{schema.get('name')}' to {lowercase_first(s=schema.get('description'))}:\n```json\n{json.dumps(schema, indent=4)}\n```"
            for schema in schemas
        ]
    )
