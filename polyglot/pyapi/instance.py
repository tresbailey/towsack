import __builtin__
import json
import uuid
from polyglot import DB
from polyglot.models.schema import Schema, Table, Field, Instance
from polyglot.pyapi import filter_fields
from polyglot.pyapi.errors import BadRequestError
from polyglot.pyapi.meta import retrieve_schema_table_fields
from polyglot.pyapi.validations import _validate, CallableClass, getitem
from polyglot.pyapi.unique import save_unique
from polyglot.pyapi.indexes import save_indexed
from polyglot.rest import remove_OIDs


def retrieve_all_instances(tenant_id, schema_id, table_id):
    """
    """
    return Instance.query.filter_by(tenant_id=tenant_id,
        schema_id=schema_id, 
        table_id=table_id).all()

def retrieve_one_instance(tenant_id, schema_id, table_id, instance_id):
    """
    """
    return Instance.query.filter_by(tenant_id=tenant_id,
        schema_id=schema_id,
        table_id=table_id,
        id=instance_id).one()


def save_instance(instance, tenant_id, schema_id, table_id, instance_id):
    instance = instance_object(id=instance_id, tenant_id=tenant_id, schema_id=schema_id, table_id=table_id, instance_data=instance)
    DB.session.add(instance)
    save_unique_values(instance, tenant_id, schema_id, table_id)
    save_index_values(instance, tenant_id, schema_id, table_id)
    DB.session.commit()
    return instance


def instance_object(filters=(), validators=Instance._validations, **instance):
    instance = filter_fields(instance, filters)
    validators['instance_data'] = create_instance_validators(instance['tenant_id'], instance['schema_id'], instance['table_id'])
    instance['schema_id'] = uuid.UUID(instance.get('schema_id', ''))
    instance['table_id'] = uuid.UUID(instance.get('table_id', ''))
    instance = Instance(**instance)
    instance.validate(validators)
    instance._validations = validators
    if (hasattr(instance, 'validation_errors') 
        and instance.validation_errors) \
    or instance.instance_data.get('validation_errors', {}): 
        instance.validation_errors = dict(instance.validation_errors.items() + instance.instance_data.get('validation_errors', {}).items())
        raise BadRequestError('Validations failed: '+ str(instance.validation_errors))
    if instance.instance_data.has_key('validation_errors'):
        del instance.instance_data['validation_errors']
    return instance


def create_instance_validators(tenant_id, schema_id, table_id):
    """
    """
    fields = retrieve_schema_table_fields(tenant_id, schema_id, table_id)
    module = __import__('polyglot.pyapi.validations', fromlist=['list_type'])
    validators = dict([(field.field_name, instance_validators(field, module)) for field in fields])
    return validators


def save_unique_values(instance, tenant_id, schema_id, table_id):
    fields = retrieve_schema_table_fields(tenant_id, schema_id, table_id)
    unique_fields  = [save_unique({field.field_name: getitem(instance.instance_data, field.field_name)}, tenant_id, schema_id, table_id, instance.id)
         for field in fields if [u'unique_field_value', u'True'] in field.constraints]
    return unique_fields
   

def save_index_values(instance, tenant_id, schema_id, table_id):
    fields = retrieve_schema_table_fields(tenant_id, schema_id, table_id)
    unique_fields  = [save_indexed({field.field_name: getitem(instance.instance_data, field.field_name)}, tenant_id, schema_id, table_id, instance.id)
         for field in fields if field.index_single]


def instance_validators(field, module):
    """
    """
    validators = []
    for constraint in field.constraints:
        funk = getattr(module, constraint[0])
        arg_type = funk.arg_type
        if callable(arg_type):
            if arg_type == CallableClass:
                arg_one = dict(tenant_id=field.tenant_id,
                    schema_id=field.schema_id, table_id=field.table_id, field_name=field.field_name)
            elif hasattr(__builtin__, constraint[1]):
                arg_one = getattr(__builtin__, constraint[1])
            else:
                arg_one = arg_type(constraint[1])
        validators.append((funk, arg_one))
    return validators
