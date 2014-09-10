import json
import uuid
from flask import Blueprint, request, Response, abort, g, make_response
from polyglot import DB
from polyglot.models.schema import Schema, Table, Field, Instance
from polyglot.pyapi.instance import retrieve_all_instances, save_instance
from polyglot.rest import remove_OIDs


instances = Blueprint('instance_apis', __name__,
    template_folder='polyglot/templates',
    static_folder='static')


@instances.route('/schemas/<schema_id>/tables/<table_id>/instances', methods=['GET'])
def get_all_instances(schema_id, table_id):
    """
    """
    return json.dumps([instance.instance_data for instance in retrieve_all_instances(schema_id, table_id)], remove_OIDs)


@instances.route('/schemas/<schema_id>/tables/<table_id>/instances', methods=['POST'])
def save_new_instance(schema_id, table_id):
    """
    """
    instance = save_instance(json.loads(request.data), schema_id, table_id, uuid.uuid4())
    return json.dumps(instance, default=remove_OIDs)

