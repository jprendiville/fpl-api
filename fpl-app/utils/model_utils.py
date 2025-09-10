from decimal import Decimal

from django.db import models
import json
import logging

from django.core.exceptions import ValidationError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BlankCharField(models.CharField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return ''
        return value

def parse_decimal(value):
    return Decimal(value).quantize(Decimal('0.00'))

def validate_json_against_model(json_data, model):
    """
    Validates JSON data against a Django model and also identifies extra fields.

    Args:
        json_data: The JSON data to be validated.
        model: The Django model to validate against.
    """

    if json_data:
        try:
            # Get model fields and ManyToMany fields separately
            model_fields = set(field.name for field in model._meta.fields)
            many_to_many_fields = set(field.name for field in model._meta.many_to_many)

            json_fields = set(json_data[0].keys())
            new_json_fields = json_fields - (model_fields | many_to_many_fields)
            if new_json_fields:
                logger.info(f"New fields in JSON for model {model.__name__}: {new_json_fields}")

            # Separate ManyToMany data
            cleaned_data = []
            many_to_many_data = []

            for data in json_data:
                for field in model._meta.fields:
                    if isinstance(field, models.DecimalField) and field.name in data:
                        value = data[field.name]
                        if value is not None:  # Skip null values
                            # Convert to string first to avoid floating-point artifacts
                            data[field.name] = Decimal(str(value))
                # Extract ManyToManyField data (e.g., element_types)
                many_to_many_entry = {key: data.pop(key) for key in many_to_many_fields if key in data}
                cleaned_data.append({key: data[key] for key in model_fields if key in data})
                many_to_many_data.append(many_to_many_entry)

            # Validate the cleaned data
            model_instances = []
            for i, cleaned_entry in enumerate(cleaned_data):
                instance = model(**cleaned_entry)
                instance.full_clean(validate_unique=False)
                instance._many_to_many_data = many_to_many_data[i]  # Attach ManyToMany data to the instance
                model_instances.append(instance)

            return model_instances

        except (json.JSONDecodeError, ValidationError) as e:
            logger.info("%s: %s", model._meta, e)
            return [model(**data_dict) for data_dict in cleaned_data]
    return []



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