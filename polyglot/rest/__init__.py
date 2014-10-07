""" All the ReSTful APIs for the app are defined as HTTP endpoints in this module """
from datetime import datetime
from flask import g, request, url_for
from polyglot import DB
from polyglot.models import AppModel
from urlparse import urlparse, urljoin

def remove_OIDs(obj):
    """
    Removes the ObjectID types from an object 
    before returning
    """
    if isinstance(obj, list):
        return [remove_OIDs(ob) for ob in obj]
    elif isinstance(obj, AppModel):
        response = obj.clean4_dump()
        if g and getattr(g, 'save_errors', None) is not None:
            response['messages'] = g.save_errors
        return response
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%s %p')

