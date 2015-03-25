""" All the ReSTful APIs for the app are defined as HTTP endpoints in this module """
import collections
from datetime import datetime
from flask import Flask, g, request, url_for, Response
from json import dumps
from polyglot import DB, APP
from polyglot.errors import BadRequestError, ResourceNotFoundException
from polyglot.models import AppModel
from polyglot.pyapi import filter_fields
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


def unwrap_response(response, **kwargs):
    """
    Order is important in the unwrap and grab.  First unwrap any vars, then filter them
    """
    if hasattr(response, '__iter__') and isinstance(response, collections.Sequence):
        new_response = [query_args(sub_res) for sub_res in response]
    else:    
        new_response = query_args(response)
    return Response(dumps(new_response, default=remove_OIDs), mimetype="application/json")


def query_args(new_response, filters=[]):
    """
    Method to unwrap and filter fields that are returned by a JSON REST response
    The 'grab' query arg is intended to be like select columns to reduce the number of fileds returned
    The 'unwrap' query arg is intended to get a field from the top level obj to be the return value
    """
    if hasattr(new_response, 'clean4_dump'):
        new_response = new_response.clean4_dump()
    for key in request.args.getlist('unwrap'):
        new_response = new_response[key]
    grab = request.args.getlist('grab') or new_response.keys()
    if grab or filters:
        grab = set(grab)
        keys = list(set(new_response.keys()) - grab)
        filters = list(set(filters) - grab)
        new_response = filter_fields(new_response, keys + filters)
    return new_response
