import json
import uuid
from flask import Blueprint, request, g, make_response
from polyglot import DB
from polyglot.models.schema import Schema, Table, Field, Instance
from polyglot.pyapi import filter_fields
from polyglot.pyapi.instance import retrieve_all_instances, retrieve_one_instance, save_instance
from polyglot.rest import unwrap_response


instances = Blueprint('instance_apis', __name__,
    template_folder='polyglot/templates',
    static_folder='static')


@instances.route('/tenants/<tenant_id>/schemas/<schema_id>/tables/<table_id>/instances', methods=['GET'])
def get_all_instances(tenant_id, schema_id, table_id):
    """
    """
    return unwrap_response([instance for instance in retrieve_all_instances(tenant_id, schema_id, table_id, query_filters=add_filter_fields())])


def add_filter_fields():
    field_list = request.args.getlist('qfield')
    value_list = request.args.getlist('qvalue')
    if len(field_list) != len(value_list):
        return dict()
    return dict(zip(field_list, value_list))


@instances.route('/tenants/<tenant_id>/schemas/<schema_id>/tables/<table_id>/instances/<instance_id>',
    methods=['GET'])
def get_one_instance(tenant_id, schema_id, table_id, instance_id):
    """
    """
    filters = ['id', 'tenant_id', 'schema_id', 'table_id']
    instance = retrieve_one_instance(tenant_id, schema_id, table_id, instance_id).clean4_dump()
    return unwrap_response(instance, filters=filters)


@instances.route('/tenants/<tenant_id>/schemas/<schema_id>/tables/<table_id>/instances', methods=['POST'])
def save_new_instance(tenant_id, schema_id, table_id):
    """
    """
    instance = save_instance(json.loads(request.data), tenant_id, schema_id, table_id, uuid.uuid4())
    return unwrap_response(instance)


@instances.route('/tenants/<tenant_id>/schemas/<schema_id>/tables/<table_id>/instances/<instance_id>', methods=['PUT'])
def update_existing_instance(tenant_id, schema_id, table_id, instance_id):
    """
    """
    instance = save_instance(json.loads(request.data), tenant_id, schema_id, table_id, instance_id)
    return unwrap_response(instance)
