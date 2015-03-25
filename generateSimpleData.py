import click
import glob
import json
import os
import plistlib
import requests

from generate.data import italy, mas as data
from polyglot.models.schema import Tenant, Schema, Table, Field, Instance
from polyglot.pyapi import filter_fields
from polyglot.rest import remove_OIDs
from collections import deque
from itertools import chain, cycle
from uuid import UUID

import pdb



@click.group()
@click.option('-r', '--system-of-record', default='local')
@click.option('-t', '--target-system', default='local')
@click.option('-c', '--copy_records', default=False)
@click.option('-p', '--plist-location', default='demoContent.plist')
@click.pass_context
def demo_content(ctx, system_of_record, target_system, copy_records, plist_location):
    """
    Main setup function for Click commands, gets all existing 
    static properties, books, file constraints, and image files
    """
    ctx.obj = {}

    domains = dict(local='http://localhost:5010', test='https://drift-t.bmwgroup.net',
        integration='https://drift-i.bmwgroup.net', prod='https://drift.bmwgroup.net')

    ctx.obj['target_url'] = target_system
    ctx.obj['headers'] = {'Content-Type': "application/json", "Accept": "application/json"}
    try:
        load_tenants(ctx)
        load_schemas(ctx)
        load_tables(ctx)
        #load_fields(ctx)
    except IndexError:
        pass


def replace_linked_props(ctx, resource, prop_replacer, linked_attributes=()):
    changes = dict([(attr, prop_replacer(*resource.get(attr, '').strip('%').split('#'))) for attr in linked_attributes if resource.get(attr, '').startswith('%')])
    resource.update(changes)
    return resource
    

def create_tenant(ctx, tenant):
    return requests.post('%s/tenants' % ctx.obj['target_url'],
        data=remove_id_tag(tenant),
        headers=ctx.obj['headers']).json()
    


@demo_content.command()
@click.pass_context
def tenants(ctx):
    ctx.obj['tenants'] = [create_tenant(ctx, tenant) 
            for tenant in data.get('tenants', [])]
    return ctx.obj['schemas']

def create_schema(ctx, schema):
    return requests.post('%s/tenants/%s/schemas' % 
        (ctx.obj['target_url'], schema['tenant_id']),
        data=remove_id_tag(schema, ('id', 'tenant_id')), headers=ctx.obj['headers']).json()


@demo_content.command()
@click.pass_context
def schemas(ctx):
    id_replacer = lambda data_key, prop_key, prop_value: next( prop['id'] for prop in ctx.obj[data_key] if prop[prop_key]==prop_value )
    schemas = [replace_linked_props(ctx, schema, id_replacer, ('tenant_id',))
            for schema in data.get('schemas', [])]
    ctx.obj['schemas'] = [create_schema(ctx, schema)
            for schema in schemas]
    return ctx.obj['schemas']

def create_table(ctx, table):
    return requests.post('%s/tenants/%s/schemas/%s/tables' % 
        (ctx.obj['target_url'], table['tenant_id'], table['schema_id']),
        data=remove_id_tag(table, ('id', 'tenant_id', 'schema_id')),
        headers=ctx.obj['headers']).json()


@demo_content.command()
@click.pass_context
def tables(ctx):
    id_replacer = lambda data_key, prop_key, prop_value: next( prop['id'] for prop in ctx.obj[data_key] if prop[prop_key]==prop_value )
    tables = [replace_linked_props(ctx, table, id_replacer, ('tenant_id', 'schema_id'))
            for table in data.get('tables', [])]
    ctx.obj['tables'] = [create_table(ctx, table)
            for table in tables]
    return ctx.obj['tables']


def create_field(ctx, field):
    return requests.post('%s/tenants/%s/schemas/%s/tables/%s/fields' % 
        (ctx.obj['target_url'], field['tenant_id'], field['schema_id'], field['table_id']),
        data=remove_id_tag(field, ('id', 'tenant_id', 'schema_id', 'table_id')),
        headers=ctx.obj['headers']).json()


@demo_content.command()
@click.pass_context
def fields(ctx):
    id_replacer = lambda data_key, prop_key, prop_value: next( prop['id'] for prop in ctx.obj[data_key] if prop[prop_key]==prop_value )
    pdb.set_trace()
    fields = [replace_linked_props(ctx, field, id_replacer, ('tenant_id', 'schema_id', 'table_id'))
            for field in data.get('fields', [])]
    ctx.obj['fields'] = [create_field(ctx, field)
            for field in fields]
    return ctx.obj['fields']


def create_instance(ctx, instance):
    return requests.post('%s/tenants/%s/schemas/%s/tables/%s/instances' % 
        (ctx.obj['target_url'], instance['tenant_id'], instance['schema_id'], instance['table_id']),
        data=remove_id_tag(instance, ('tenant_id', 'schema_id', 'table_id')),
        headers=ctx.obj['headers']).json()


@demo_content.command()
@click.pass_context
def instances(ctx):
    id_replacer = lambda data_key, prop_key, prop_value: next( prop['id'] for prop in ctx.obj[data_key] if prop[prop_key]==prop_value )
    instances = [replace_linked_props(ctx, instance, id_replacer, ('tenant_id', 'schema_id', 'table_id'))
            for instance in data.get('instances', [])]
    ctx.obj['instances'] = [create_instance(ctx, instance)
            for instance in instances]
    return ctx.obj['instances']
   

def remove_id_tag(orm, fields=('id',)):
    return json.dumps(filter_fields(json.loads(json.dumps(orm, default=remove_OIDs)), fields))


@click.pass_context
def load_tenants(ctx):
    ctx.obj['tenants'] = requests.get('%s/tenants' % ctx.obj['target_url']).json()
    return ctx.obj['tenants']


@click.pass_context
def load_schemas(ctx):
    schemas = [requests.get('%s/tenants/%s/schemas' % 
        (ctx.obj['target_url'], tenant['id'])).json() for tenant in ctx.obj['tenants']]
    ctx.obj['schemas'] = [ item for sublist in schemas for item in sublist]
    return ctx.obj['schemas']


@click.pass_context
def load_tables(ctx):
    tables = [requests.get('%s/tenants/%s/schemas/%s/tables' % 
        (ctx.obj['target_url'], schema['tenant_id'], schema['id'])).json() for schema in ctx.obj['schemas']]
    ctx.obj['tables'] = [ item for sublist in tables for item in sublist]
    return ctx.obj['tables']


@click.pass_context
def load_fields(ctx):
    fields = [requests.get('%s/tenants/%s/schemas/%s/tables/%s/fields' % 
        (ctx.obj['target_url'], table['tenant_id'], table['schema_id'], table['id'])).json() for table in ctx.obj['tables']]
    ctx.obj['fields'] = [ item for sublist in fields for item in sublist]
    return ctx.obj['fields']


if __name__ == '__main__':
    demo_content()
