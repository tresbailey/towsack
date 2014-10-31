from bson.errors import InvalidId
from flask import Blueprint, Response
from polyglot import APP
from polyglot.errors import BadRequestError, ResourceNotFoundException


@APP.errorhandler(BadRequestError)
def handle_excpetions(error):
    return Response(error.msg, 400)


@APP.errorhandler(ResourceNotFoundException)
def handle_not_found(error):
    return Response(error.msg, 404)

@APP.errorhandler(InvalidId)
def handle_bad_id(error):
    return Response('The ID provided, %s, was not valid' % error.message.split(' ',1)[0], 400)
