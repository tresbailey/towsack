import json
import uuid
from polyglot import DB, MEM, APP
from polyglot.models.schema import Tenant, Schema, Table, Field, Instance
from polyglot.pyapi import filter_fields
from polyglot.rest import remove_OIDs


def retrieve_all_tenants():
    return Tenant.query.all()


def save_tenant(tenant, tenant_id):
    tenant = tenant_object(id=tenant_id, **tenant)
    DB.session.add(tenant)
    DB.session.commit()
    return tenant


def retrieve_all_schemas(tenant_id):
    """
    All
    """
    return Schema.query.filter_by(tenant_id=tenant_id).all()


def save_schema(schema, tenant_id, schema_id):
    """
    Save one
    """
    schema = schema_object(id=schema_id, tenant_id=tenant_id, **schema)
    DB.session.add(schema)
    DB.session.commit()
    return schema


def retrieve_schema_tables(tenant_id, schema_id):
    """
    """
    return Table.query.filter_by(schema_id=schema_id).all()


def save_table(table, tenant_id, schema_id, table_id):
    """
    """
    table = table_object(id=table_id, schema_id=schema_id, **table)
    DB.session.add(table)
    DB.session.commit()
    return table


def retrieve_schema_table(tenant_id, schema_id, table_id):
    """
    """
    return Table.query.filter_by(schema_id=schema_id, id=table_id).one()


def retrieve_schema_table_fields(tenant_id, schema_id, table_id):
    """
    """
    return Field.query.filter_by(table_id=table_id, schema_id=schema_id).all()

    
def save_field(field, tenant_id, schema_id, table_id, field_id):
    field = field_object(id=field_id, tenant_id=tenant_id, table_id=table_id, schema_id=schema_id, **field)
    DB.session.add(field)
    DB.session.commit()
    cache_field_by_name(field, tenant_id, schema_id, table_id, field_id)
    return field


def cache_field_by_name(field, tenant_id, schema_id, table_id, field_id):
    key = '%s:%s:%s' % (schema_id, table_id, field.field_name)
    MEM.hset(APP.config['REDIS_HASH_FBN'], key, json.dumps(field, default=remove_OIDs))


def tenant_object(filters=(), validators=Tenant._validations, **tenant):
    tenant = filter_fields(tenant, filters)
    tenant['schemas'] = [schema_object(**schema) for schema in tenant.get('schemas', [])]
    tenant = Tenant(**tenant)
    tenant.validate(validators)
    return tenant


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
