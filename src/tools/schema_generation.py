from pydantic.json_schema import GenerateJsonSchema


class MyGenerateJsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode="validation"):
        json_schema = super().generate(schema, mode=mode)

        # Remove titles
        json_schema.pop("title", None)

        # Reorder properties to have type and description first
        for property_schema in json_schema.get("properties", {}).values():
            property_schema.pop("title", None)

            # Reorder each property schema
            ordered_property = {}

            # Add type first if exists
            if "type" in property_schema:
                ordered_property["type"] = property_schema.pop("type")

            # Add description second if exists
            if "description" in property_schema:
                ordered_property["description"] = property_schema.pop("description")

            # Add remaining fields
            ordered_property.update(property_schema)
            property_schema.clear()
            property_schema.update(ordered_property)

        # Create ordered top-level structure
        ordered_schema = {"name": json_schema.pop("name", ""), "description": json_schema.pop("description", "")}

        # Create parameters with specific order
        parameters = {
            "type": json_schema.pop("type", "object"),
            "properties": json_schema.pop("properties", {}),
            "required": json_schema.pop("required", []),
        }

        ordered_schema["parameters"] = parameters
        return ordered_schema
