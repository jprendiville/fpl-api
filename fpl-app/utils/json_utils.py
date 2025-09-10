import json


def formatted_json(json_data):
    """
    Validates and parses a JSON string. Attempts to clean single quotes if validation fails.

    Args:
        json_data (str): The JSON string to validate and parse.

    Returns:
        dict or list: Parsed JSON data.

    Raises:
        ValueError: If the JSON string is invalid, even after attempting cleanup.
    """
    try:
        return json.loads(json_data)
    except json.JSONDecodeError:
        cleaned_json = json_data.replace("'", '"')
        return json.loads(cleaned_json)