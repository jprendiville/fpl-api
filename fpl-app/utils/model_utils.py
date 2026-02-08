from decimal import Decimal

from django.db import models
from django.apps import apps
import json
import logging

from django.core.exceptions import ValidationError

from utils.string_utils import singularize

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class BlankCharField(models.CharField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return ''
        return value


def parse_decimal(value):
    return Decimal(value).quantize(Decimal('0.00'))


def validate_json_against_model(json_data, model, parent_model=None):
    """
    Validates JSON data against a Django model and also identifies extra fields.

    - If a JSON field is not on the model, we check whether a related model exists.
      Example: Player + scout_risks → PlayerScoutRisk
    - If the related model exists, we validate nested items against that model.
    - If the related model does NOT exist, we log it as a new field.
    - Nested fields are preserved on the instance as _extra_fields.
    """

    if not json_data:
        return []

    try:
        if parent_model is None:
            parent_model = model

        # Model fields and M2M fields
        model_fields = set(field.name for field in model._meta.fields)
        many_to_many_fields = set(field.name for field in model._meta.many_to_many)

        # Collect all JSON fields across all rows
        json_fields = set().union(*(d.keys() for d in json_data))

        # Fields not in the model
        new_json_fields = json_fields - (model_fields | many_to_many_fields)

        # Detect nested fields: list containing dicts in ANY row
        nested_fields = {}
        for key in json_fields:
            for row in json_data:
                value = row.get(key)
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    nested_fields[key] = value
                    break

        # Primitive new fields = not model fields, not M2M, not nested
        primitive_new_fields = new_json_fields - set(nested_fields.keys())
        if primitive_new_fields:
            logger.info(
                f"New primitive fields in JSON for model {model.__name__}: {primitive_new_fields}"
            )

        # Validate nested fields against related models
        for key, nested_list in nested_fields.items():
            if isinstance(nested_list, list) and len(nested_list) == 0:
                continue

            singular = singularize(key)
            related_model_name = f"{model.__name__}{''.join(part.capitalize() for part in singular.split('_'))}"

            try:
                related_model = apps.get_model(
                    app_label=model._meta.app_label,
                    model_name=related_model_name
                )
            except LookupError:
                logger.info(
                    f"Nested field '{key}' has no matching model '{related_model_name}'"
                )
                continue

            # Validate each nested item structurally
            for item in nested_list:
                try:
                    validate_json_against_model([item], related_model, parent_model=parent_model)
                except Exception as e:
                    logger.info(
                        f"Validation error in nested field '{key}' for model '{related_model_name}': {e}"
                    )

        # If this is a nested model, stop here: don't build instances
        if model is not parent_model:
            return []

        cleaned_data = []
        many_to_many_data = []
        extra_fields_list = []

        # Process each JSON object
        for data in json_data:

            # Convert DecimalFields safely
            for field in model._meta.fields:
                if isinstance(field, models.DecimalField) and field.name in data:
                    value = data[field.name]
                    if value is not None:
                        data[field.name] = Decimal(str(value))

            # Extract ManyToManyField data
            m2m_entry = {key: data.pop(key) for key in many_to_many_fields if key in data}
            many_to_many_data.append(m2m_entry)

            # Extract model fields
            cleaned_entry = {key: data[key] for key in model_fields if key in data}
            cleaned_data.append(cleaned_entry)

            # Preserve nested fields for ingestion
            extra_fields = {key: data[key] for key in nested_fields if key in data}
            extra_fields_list.append(extra_fields)

        # Validate cleaned data (top-level only)
        model_instances = []
        for i, cleaned_entry in enumerate(cleaned_data):
            instance = model(**cleaned_entry)
            instance.full_clean(validate_unique=False)

            instance._many_to_many_data = many_to_many_data[i]
            instance._extra_fields = extra_fields_list[i]

            model_instances.append(instance)

        return model_instances

    except (json.JSONDecodeError, ValidationError) as e:
        logger.info("%s: %s", model._meta, e)
        return [model(**data_dict) for data_dict in cleaned_data]


class BaseModel(models.Model):
    """
    Base model that adds flexibility to optionally skip uniqueness validation in full_clean.
    """
    class Meta:
        abstract = True  # This makes sure Django won't create a table for this model

    def full_clean(self, exclude=None, validate_unique=True):
        """
        Override full_clean to optionally skip uniqueness validation.
        """

        # Ensure exclude is a list
        exclude = exclude or []
        if not isinstance(exclude, list):
            exclude = list(exclude)

        # Dynamically exclude fields based on unique constraints
        for constraint in self._meta.constraints:
            if isinstance(constraint, models.UniqueConstraint):
                exclude.extend(constraint.fields)

        super().full_clean(exclude=exclude, validate_unique=validate_unique)