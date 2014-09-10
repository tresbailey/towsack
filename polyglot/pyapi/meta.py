import json
import uuid
from polyglot import DB, MEM, APP
from polyglot.models.schema import Schema, Table, Field, Instance
from polyglot.pyapi import filter_fields
from polyglot.rest import remove_OIDs


def retrieve_all_schemas():
    """
    All
    """
    return Schema.query.all()


def save_schema(schema, schema_id):
    """
    Save one
    """
    schema = schema_object(id=schema_id, **schema)
    DB.session.add(schema)
    DB.session.commit()
    return schema


def retrieve_schema_tables(schema_id):
    """
    """
    return Table.query.filter_by(schema_id=schema_id).all()


def save_table(table, schema_id, table_id):
    """
    """
    table = table_object(id=table_id, schema_id=schema_id, **table)
    DB.session.add(table)
    DB.session.commit()
    return table


def retrieve_schema_table(schema_id, table_id):
    """
    """
    return Table.query.filter_by(schema_id=schema_id, id=table_id).one()


def retrieve_schema_table_fields(schema_id, table_id):
    """
    """
    return Field.query.filter_by(table_id=table_id, schema_id=schema_id).all()

    
def save_field(field, schema_id, table_id, field_id):
    import pdb
    pdb.set_trace()
    field = field_object(id=field_id, table_id=table_id, schema_id=schema_id, **field)
    DB.session.add(field)
    DB.session.commit()
    cache_field_by_name(field, schema_id, table_id, field_id)
    return field


def cache_field_by_name(field, schema_id, table_id, field_id):
    key = '%s:%s:%s' % (schema_id, table_id, field.field_name)
    MEM.hset(APP.config['REDIS_HASH_FBN'], key, json.dumps(field, default=remove_OIDs))


def schema_object(filters=(), validators=Schema._validations, **schema):
    schema = filter_fields(schema, filters)
    schema['tables'] = [table_object(**table) for table in schema.get('tables', [])]
    schema = Schema(**schema)
    schema.validate(validators)
    return schema


def table_object(filters=(), validators=Table._validations, **table):
    table = filter_fields(table, filters)
    table['fields'] = [field_object(**field) for field in table.get('fields', [])]
    table = Table(**table)
    table.validate(validators)
    return table


def field_object(filters=(), validators=Field._validations, **field):
    field = filter_fields(field, filters)
    field = Field(**field)
    field.validate(validators)
    return field
