import __builtin__
import json
import uuid
from polyglot import DB
from polyglot.models.schema import Schema, Table, Field, Instance
from polyglot.pyapi import filter_fields
from polyglot.pyapi.errors import BadRequestError
from polyglot.pyapi.meta import retrieve_schema_table_fields
from polyglot.pyapi.validations import _validate
from polyglot.rest import remove_OIDs


def retrieve_all_instances(schema_id, table_id):
    """
    """
    return Instance.query.filter_by(schema_id=schema_id, table_id=table_id).all()


def save_instance(instance, schema_id, table_id, instance_id):
    instance = instance_object(id=instance_id, schema_id=schema_id, table_id=table_id, instance_data=instance)
    DB.session.add(instance)
    DB.session.commit()
    return instance


def instance_object(filters=(), validators=Instance._validations, **instance):
    instance = filter_fields(instance, filters)
    validators['instance_data'] = create_instance_validators(instance['schema_id'], instance['table_id'])
    instance['schema_id'] = uuid.UUID(instance.get('schema_id', ''))
    instance['table_id'] = uuid.UUID(instance.get('table_id', ''))
    instance = Instance(**instance)
    instance.validate(validators)
    if (hasattr(instance, 'validation_errors') 
        and instance.validation_errors) \
    or instance.instance_data.get('validation_errors', {}): 
        instance.validation_errors = dict(instance.validation_errors.items() + instance.instance_data.get('validation_errors', {}).items())
        raise BadRequestError('Validations failed: '+ str(instance.validation_errors))
    if instance.instance_data.has_key('validation_errors'):
        del instance.instance_data['validation_errors']
    return instance


def create_instance_validators(schema_id, table_id):
    """
    """
    fields = retrieve_schema_table_fields(schema_id, table_id)
    module = __import__('polyglot.pyapi.validations', fromlist=['list_type'])
    validators = dict([(field.field_name, instance_validators(field.constraints, module)) for field in fields])
    return validators


def instance_validators(constraints, module):
    """
    """
    validators = []
    for constraint in constraints:
        funk = getattr(module, constraint[0])
        arg_type = funk.arg_type
        if callable(arg_type):
            if hasattr(__builtin__, constraint[1]):
                arg_one = getattr(__builtin__, constraint[1])
            else:
                arg_one = arg_type(constraint[1])
        validators.append((funk, arg_one))
    return validators
