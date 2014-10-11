import uuid
from polyglot import DB
from polyglot.models.schema import Index
from polyglot.pyapi import filter_fields
from polyglot.pyapi.errors import BadRequestError
from polyglot.pyapi.validations import getitem
from sqlalchemy.sql import exists
from sqlalchemy.sql.elements import or_


def add_index_query_filter(indexed_field, search_value):
    """
    Adds Alchemy filter criteria for each of the fields of an Instance query
    """
    return Index.index_value.contains({indexed_field: search_value})



def save_indexed(indexed_value, tenant_id, schema_id, table_id, instance_id, auto_commit=False):
    indexed_value = indexed_object(id=uuid.uuid4(), tenant_id=tenant_id,
        schema_id=schema_id, table_id=table_id,
        instance_id=instance_id, index_value=indexed_value)
    DB.session.add(indexed_value)
    if auto_commit:
        DB.session.commit()
    return indexed_value


def indexed_object(filters=(), validators=Index._validations, **indexed):
    indexed = filter_fields(indexed, filters)
    indexed = Index(**indexed)
    indexed.validate(validators)
    return indexed
