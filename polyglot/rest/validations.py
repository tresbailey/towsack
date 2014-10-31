from flask import Blueprint
from polyglot.errors import ResourceNotFoundException
from polyglot.rest import unwrap_response


val_funks = Blueprint('validation_functions', __name__, 
    template_folder='polyglot/templates',
    static_folder='static')


@val_funks.route('/validations/<funk_name>/docs', methods=['GET'])
def function_doc(funk_name):
    """
    Returns the docstring of the function requested by name
    :param funk_name: Name of the function to get the docstring from
    :type funk_name: str
    :returns: dict -- Object with the docstring as the message attribute
    """
    try:
        module = __import__('polyglot.pyapi.validations', fromlist=[funk_name])
        funk = getattr(module, funk_name)
        return unwrap_response(dict(docstring=funk.func_doc))
    except AttributeError:
        raise ResourceNotFoundException("The function, %s, does not exist as a validation" % funk_name)
