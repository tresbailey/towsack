import json
import uuid
from flask import Blueprint, request, Response, abort, g, make_response
from polyglot import DB
from polyglot.models.schema import Schema, Table, Field, Instance
from polyglot.pyapi.meta import retrieve_all_tenants, save_tenant, retrieve_all_schemas, \
    save_schema, retrieve_schema_tables, save_table, retrieve_schema_table, \
    retrieve_schema_table_fields, save_field
from polyglot.rest import remove_OIDs


meta = Blueprint('meta_apis', __name__,
        template_folder='polyglot/templates', static_folder='static')


@meta.route('/tenants', methods=['GET'])
def get_all_tenants():
    """
    Retrieves all the tenant definitions
    """
    return json.dumps(retrieve_all_tenants(),
        default=remove_OIDs)


@meta.route('/tenants', methods=['POST'])
def create_new_tenant():
    tenant = save_tenant(json.loads(request.data), uuid.uuid4())
    return json.dumps(tenant, default=remove_OIDs)


@meta.route('/tenants/<tenant_id>/schemas', methods=['GET'])
def get_all_schemas(tenant_id):
    """
    Retrieves all the schema definitions
    """
    return json.dumps(retrieve_all_schemas(tenant_id), 
        default=remove_OIDs)


@meta.route('/tenants/<tenant_id>/schemas', methods=['POST'])
def create_new_schema(tenant_id):
    """
    Create a new schema definition
    """
    schema = save_schema(json.loads(request.data), tenant_id, uuid.uuid4())
    return json.dumps(schema, default=remove_OIDs)


@meta.route('/tenants/<tenant_id>/schemas/<schema_id>/tables', methods=['GET'])
def get_schema_tables(tenant_id, schema_id):
    """
    Retrieves the Tables for a Schema
    """
    return json.dumps(retrieve_schema_tables(tenant_id, uuid.UUID(schema_id)), default=remove_OIDs)


@meta.route('/tenants/<tenant_id>/schemas/<schema_id>/tables', methods=['POST'])
def create_schema_table(tenant_id, schema_id):
    """
    Retrieves the Tables for a Schema
    """
    table = save_table(json.loads(request.data), uuid.UUID(tenant_id), uuid.UUID(schema_id), uuid.uuid4())
    return json.dumps(table, default=remove_OIDs)


@meta.route('/tenants/<tenant_id>/schemas/<schema_id>/tables/<table_id>', methods=['GET'])
def get_table(tenant_id, schema_id, table_id):
    """
    Retrieves the table and its fields
    """
    return json.dumps(retrieve_schema_table(tenant_id, schema_id, table_id), default=remove_OIDs)


@meta.route('/tenants/<tenant_id>/schemas/<schema_id>/tables/<table_id>/fields', methods=['GET'])
def get_table_fields(tenant_id, schema_id, table_id):
    return json.dumps(retrieve_schema_table_fields(tenant_id, schema_id, table_id), default=remove_OIDs)


@meta.route('/tenants/<tenant_id>/schemas/<schema_id>/tables/<table_id>/fields', methods=['POST'])
def save_table_fields(tenant_id, schema_id, table_id):
    """
    """
    field = save_field(json.loads(request.data), tenant_id, schema_id, table_id, uuid.uuid4())
    return json.dumps(field, default=remove_OIDs)
