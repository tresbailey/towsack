from polyglot.alchemy import GUID
from polyglot.models import AppModel
from polyglot.pyapi.validations import is_type, list_type, not_empty, min_length, dict_type
from sqlalchemy import Table, Column, Boolean, String, ForeignKey, Enum, Integer, Boolean, UniqueConstraint, Index as Alchemy_Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, NUMERIC
from uuid import UUID


class Instance(AppModel):
    __tablename__ = 'instances'
    id = Column(GUID, primary_key=True)
    tenant_id = Column(GUID, ForeignKey('tenants.id'))
    schema_id = Column(GUID, ForeignKey('schemas.id'))
    table_id = Column(GUID, ForeignKey('tables.id'))
    instance_data = Column(JSONB)
    _validations = {
        'schema_id': ((is_type, UUID),),
        'table_id': ((is_type, UUID),)
    }


class Unique(AppModel):
    __tablename__ = 'uniques'
    id = Column(GUID, primary_key=True)
    tenant_id = Column(GUID, ForeignKey('tenants.id'))
    schema_id = Column(GUID, ForeignKey('schemas.id'))
    table_id = Column(GUID, ForeignKey('tables.id'))
    instance_id = Column(GUID, ForeignKey('instances.id'))
    unique_value = Column(JSONB)
    _validations = {
        'tenant_id': ((is_type, UUID),),
        'schema_id': ((is_type, UUID),),
        'table_id': ((is_type, UUID),),
        'instance_id': ((is_type, UUID),),
        'unique_value': ((is_type, dict), (not_empty, True))
    }
    __table_args__ = (UniqueConstraint('table_id', 'schema_id', 'tenant_id', 'unique_value', name='unique_table_unique'),)


class Index(AppModel):
    __tablename__ = 'indexes'
    id = Column(GUID, primary_key=True)
    tenant_id = Column(GUID, ForeignKey('tenants.id'))
    schema_id = Column(GUID, ForeignKey('schemas.id'))
    table_id = Column(GUID, ForeignKey('tables.id'))
    instance_id = Column(GUID, ForeignKey('instances.id'))
    index_value = Column(JSONB)
    _validations = {
        'tenant_id': ((is_type, UUID),),
        'schema_id': ((is_type, UUID),),
        'table_id': ((is_type, UUID),),
        'instance_id': ((is_type, UUID),),
        'index_value': ((is_type, dict), (not_empty, True))
    }


class Field(AppModel):
    __tablename__ = 'fields'
    id = Column(GUID, primary_key=True)
    field_name = Column(String)
    table_id = Column(GUID, ForeignKey('tables.id'))
    schema_id = Column(GUID, ForeignKey('schemas.id'))
    tenant_id = Column(GUID, ForeignKey('tenants.id'))
    constraints = Column(ARRAY(String))
    index_single = Column(Boolean)
    _validations = {
        'field_name': ((is_type, str),),
        'table_id': ((is_type, UUID),),
        'constraints': ((list_type, tuple), (not_empty, True), (min_length, 1))
    }
    __table_args__ = (UniqueConstraint('field_name', 'table_id', 'schema_id', name='unique_table_field'),)
    

class Table(AppModel):
    __tablename__ = 'tables'
    id = Column(GUID, primary_key=True)
    table_name = Column(String)
    schema_id = Column(GUID, ForeignKey('schemas.id'))
    tenant_id = Column(GUID, ForeignKey('tenants.id'))
    fields = relationship('Field', backref='table')
    _validations = {
        'table_name': ((is_type, str),),
        'schema_id': ((is_type, UUID),),
        'fields': ((list_type, Field),),
    }
    __table_args__ = (UniqueConstraint('table_name', 'schema_id', name='unique_schema_table'),)


class Schema(AppModel):
    __tablename__ = 'schemas'
    id = Column(GUID, primary_key=True)
    schema_name = Column(String)
    tables = relationship('Table', backref='schema')
    tenant_id = Column(GUID, ForeignKey('tenants.id'))
    _validations = {
        'schema_name': ((is_type, str),),
        'tables': ((list_type, Table),)
    }

class Tenant(AppModel):
    __tablename__ = 'tenants'
    id = Column(GUID, primary_key=True)
    tenant_name = Column(String)
    schemas = relationship('Schema', backref='tenant')
    _validations = {
        'tenant_name': ((is_type, str),),
        'schemas': ((list_type, Schema),)
    }
