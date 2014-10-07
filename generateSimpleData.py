import click
import glob
import json
import os
import plistlib
import requests

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

    ctx.obj['target_url'] = domains[target_system]
    ctx.obj['headers'] = {'Content-Type': "application/json", "Accept": "application/json"}
    try:
        load_tenants(ctx)
        load_schemas(ctx)
        load_tables(ctx)
        load_fields(ctx)
    except IndexError:
        pass
    

@demo_content.command()
@click.pass_context
def tenants(ctx):
    tenant = Tenant(tenant_name="Global")
    tenant = requests.post('%s/tenants' % ctx.obj['target_url'],
        data=remove_id_tag(tenant),
        headers=ctx.obj['headers']).json()
    ctx.obj['tenants'] = [tenant]
    return tenant


@demo_content.command()
@click.pass_context
def schemas(ctx):
    schema = Schema(tenant_id=ctx.obj['tenants'][0]['id'], schema_name='main_schema')
    schema = requests.post('%s/tenants/%s/schemas' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id']), 
        data=remove_id_tag(schema, ('id', 'tenant_id')), headers=ctx.obj['headers']).json()
    ctx.obj['schemas'] = [schema]
    return schema

@demo_content.command()
@click.pass_context
def tables(ctx):
    table = Table(tenant_id=ctx.obj['tenants'][0]['id'], schema_id=ctx.obj['schemas'][0]['id'], table_name='FIRST')
    table = requests.post('%s/tenants/%s/schemas/%s/tables' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id'], ctx.obj['schemas'][0]['id']),
        data=remove_id_tag(table, ('id', 'tenant_id', 'schema_id')),
        headers=ctx.obj['headers']).json()
    ctx.obj['tables'] = [table]
    table = Table(tenant_id=ctx.obj['tenants'][0]['id'], schema_id=ctx.obj['schemas'][0]['id'], table_name='SECOND')
    table = requests.post('%s/tenants/%s/schemas/%s/tables' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id'], ctx.obj['schemas'][0]['id']),
        data=remove_id_tag(table, ('id', 'tenant_id', 'schema_id')),
        headers=ctx.obj['headers']).json()
    ctx.obj['tables'].append(table)
    return ctx.obj['tables']


@demo_content.command()
@click.pass_context
def fields(ctx):
    table = ctx.obj['tables'][0]
    # List of String Field
    field = Field(schema_id=ctx.obj['schemas'][0]['id'], table_id=ctx.obj['tables'][0]['id'], field_name='STRING_LIST', constraints=[["list_type","basestring"],["min_length","1"]], index_single=False)
    field = remove_id_tag(field, ('id', 'tenant_id', 'schema_id', 'table_id'))
    field = requests.post('%s/tenants/%s/schemas/%s/tables/%s/fields' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id'], ctx.obj['schemas'][0]['id'], ctx.obj['tables'][0]['id']),
        data=field,
        headers=ctx.obj['headers']).json()
    ctx.obj['fields'] = [field]
    # String Field
    field = Field(schema_id=ctx.obj['schemas'][0]['id'], table_id=ctx.obj['tables'][0]['id'], field_name='BASIC_STRING', constraints=[("is_type","basestring")], index_single=True)
    field = requests.post('%s/tenants/%s/schemas/%s/tables/%s/fields' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id'], ctx.obj['schemas'][0]['id'], ctx.obj['tables'][0]['id']),
        data=remove_id_tag(field, ('id', 'tenant_id', 'schema_id', 'table_id')),
        headers=ctx.obj['headers']).json()
    ctx.obj['fields'].append(field)
    # Int Field
    field = Field(schema_id=ctx.obj['schemas'][0]['id'], table_id=ctx.obj['tables'][0]['id'], field_name='BASIC_INT', constraints=[["is_type","int"], ["unique_field_value", 'True']], index_single=False)
    field = requests.post('%s/tenants/%s/schemas/%s/tables/%s/fields' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id'], ctx.obj['schemas'][0]['id'], ctx.obj['tables'][0]['id']),
        data=remove_id_tag(field, ('id', 'tenant_id', 'schema_id', 'table_id')),
        headers=ctx.obj['headers']).json()
    ctx.obj['fields'].append(field)
    return ctx.obj['fields']


@demo_content.command()
@click.pass_context
def instances(ctx):
    table = ctx.obj['tables'][0]
    instance = {"BASIC_STRING":"TRES PASS 1","STRING_LIST":["val1","val2","val3"],"BASIC_INT":1010}
    instance = requests.post('%s/tenants/%s/schemas/%s/tables/%s/instances' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id'], ctx.obj['schemas'][0]['id'], ctx.obj['tables'][0]['id']),
        data=remove_id_tag(instance, ('id', 'tenant_id', 'schema_id', 'table_id')),
        headers=ctx.obj['headers']).json()


def remove_id_tag(orm, fields=('id',)):
    return json.dumps(filter_fields(json.loads(json.dumps(orm, default=remove_OIDs)), fields))


@click.pass_context
def load_tenants(ctx):
    ctx.obj['tenants'] = requests.get('%s/tenants' % ctx.obj['target_url']).json()
    return ctx.obj['tenants']


@click.pass_context
def load_schemas(ctx):
    ctx.obj['schemas'] = requests.get('%s/tenants/%s/schemas' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id'])).json()
    return ctx.obj['schemas']


@click.pass_context
def load_tables(ctx):
    ctx.obj['tables'] = requests.get('%s/tenants/%s/schemas/%s/tables' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id'], ctx.obj['schemas'][0]['id'])).json()
    return ctx.obj['tables']


@click.pass_context
def load_fields(ctx):
    ctx.obj['fields'] = requests.get('%s/tenants/%s/schemas/%s/tables/%s/fields' % 
        (ctx.obj['target_url'], ctx.obj['tenants'][0]['id'], ctx.obj['schemas'][0]['id'], ctx.obj['tables'][0]['id'])).json()
    return ctx.obj['fields']


if __name__ == '__main__':
    demo_content()
