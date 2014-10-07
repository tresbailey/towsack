import uuid
from polyglot import DB
from sqlalchemy.ext.declarative import AbstractConcreteBase

def json_clean(field_value):
    """
    Removes the ObjectID types from an object
    before returning
    """
    if isinstance(field_value,
            uuid.UUID):
        return str(field_value)
    #elif isinstance( field_value,
    #        Value):
    #    return field_value.value
    elif isinstance( field_value, list) or isinstance( field_value, tuple):
        return [ json_clean(value) for value in field_value ]
    elif isinstance( field_value,
            dict):
        return dict( [ (str(key), json_clean(value)) for key, value in field_value.items() ])
    return field_value
   

class AppModel(AbstractConcreteBase, DB.Model):
    filter_fields = ('validate', 'clean4_dump', 'get', 'instance_data', 'table', 'query_class', 'has_key', 'filter_out_fields', 'filter_fields', 'query', 'type', 'metadata')

    @classmethod
    def has_key(cls, key):
        return hasattr(cls, key)

    @classmethod
    def get(cls, key, default=None):
        return getattr(cls, key) or default

    def filter_out_fields(self, remove_keys):
        return dict([(key_, getattr(self, key_))
            for key_ in self.get_fields().iterkeys()
            if key_ not in remove_keys and hasattr(self, key_)
            ])

    def clean4_dump(self):
        """
        Removes the ObjectID types from an object
        before returning
        """
        response = {}
        for field in self.__table__.columns:
            try:
                field_value = getattr(self, field.name)
                response[field.name] = json_clean(field_value)
            except AttributeError:
                continue
        response = dict([(key, value) for key, value in response.items() if key not in [field for field in self.filter_fields]])
        return response

