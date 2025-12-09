import json
from datetime import date, datetime
from decimal import Decimal
from django.db.models import QuerySet, Model
from django.forms.models import model_to_dict

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


def to_primitive(obj, _seen=None):
    ''' minimal, defensive conversion to JSON-serializable primitives '''
    if _seen is None:
        _seen = set()

    # base cases
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, Decimal):
        return float(obj)  # or str(obj) if you prefer exact string
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    # containers
    if isinstance(obj, dict):
        return {str(k): to_primitive(v, _seen) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set, QuerySet)):
        return [to_primitive(x, _seen) for x in obj]

    # Django model -> dict of fields
    if isinstance(obj, Model):
        return to_primitive(model_to_dict(obj), _seen)

    # prevent cycles
    oid = id(obj)
    if oid in _seen:
        return None  # or f"<circular:{type(obj).__name__}>"
    _seen.add(oid)

    # generic Python object: use its public attributes
    if hasattr(obj, "__dict__"):
        data = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return {k: to_primitive(v, _seen) for k, v in data.items()}

    # last resort: string form
    return str(obj)
