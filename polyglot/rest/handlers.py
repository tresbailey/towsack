from bson.errors import InvalidId
from flask import Blueprint, Response
from polyglot import APP
from polyglot.errors import BadRequestError, ResourceNotFoundException

errors = Blueprint('error_objects', __name__,
    template_folder='polyglot/templates',
    static_folder='static')

@APP.errorhandler(BadRequestError)
def handle_excpetions(error):
    return Response(error.msg, 400)


@errors.errorhandler(ResourceNotFoundException)
def handle_not_found(error):
    return Response(error.msg, 404)

@errors.errorhandler(InvalidId)
def handle_bad_id(error):
    return Response('The ID provided, %s, was not valid' % error.message.split(' ',1)[0], 400)
