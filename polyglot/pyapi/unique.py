import uuid
from polyglot import DB
from polyglot.models.schema import Unique
from polyglot.pyapi import filter_fields
from polyglot.pyapi.errors import BadRequestError
from polyglot.pyapi.validations import getitem
from sqlalchemy.sql import exists
from sqlalchemy.sql.elements import and_


def value_combo_exists(value, **kwargs):
    """ Queries the database for any values in the unique store that alrdeady exist with given value and metadata combo
    """
    kwargs['unique_value'] = {kwargs['field_name']: value}
    del kwargs['field_name']
    filters = [(getitem(Unique, arg_name) == arg_val) for arg_name, arg_val in kwargs.items()]
    return DB.session.query(Unique.query.exists().where(and_(*filters))).scalar()


def save_unique(unique_value, tenant_id, schema_id, table_id, instance_id, auto_commit=False):
    unique = unique_object(id=uuid.uuid4(), tenant_id=tenant_id, 
        schema_id=schema_id, table_id=table_id, 
        instance_id=instance_id, unique_value=unique_value)
    DB.session.add(unique)
    if auto_commit:
        DB.session.commit()
    return unique



def unique_object(filters=(), validators=Unique._validations, **unique):
    unique = filter_fields(unique, filters)
    unique = Unique(**unique)
    unique.validate(validators)
    return unique



