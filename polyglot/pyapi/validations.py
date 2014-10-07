import re
from email.utils import parseaddr
from functools import partial
from operator import ge
from polyglot.models import AppModel
from types import FunctionType
from urlparse import urlparse


def in_list(verifield, checklist):
    """ Checks whether an item is in a list of other items
    
    :param verifield: Value of the field that is being validated
    :param checklist: Acceptable values for the field
    :type checklist: list
    :returns: bool -- True if the verifield value exists in the checklist; otherwise, False
    """
    return verifield in checklist


in_list.arg_type = list


def not_empty(verifield, required):
    """Checks if an item contains data

    :param verifield: Value of the field that is being validated
    :param required: False values negate checking the verifield
    :type required: bool
    :returns: bool -- True if verifield is non-empty; otherwise ('',[],{},(),None), False
    """
    if not required: return True
    return not not verifield and verifield is not None


not_empty.arg_type = bool


def in_zip_list(verifield, checklist):
    """Checks if a 2-tuple's values each equal some 2-tuple in a given list

    :param checklist: List of 2-tuples that the verifield should equal at least one of
    :type checklist: list
    :returns: bool -- True if verifield equals a 2-tuple in checklist; otherwise, False
    """
    valid_dims = zip( *checklist )
    return verifield[0] in valid_dims[0] and verifield[1] in valid_dims[1]


in_zip_list.arg_type = list


def range_match(verifield, ranges):
    """ Checks if an items subfields are within a given range"""
    return verifield[0] >= ranges[0][0] and verifield[0] <= ranges[0][1] and verifield[1] >= ranges[1][0] and verifield[1] <= ranges[1][1]


range_match.arg_type = list
    

def dict_type(verifield, required):
    """ Verifies that verifield is an dict type, and either has all values of required type or is an empty object
    
    :param required: Type of the value in a dict, where the key of the dict is always a str type
    :type required: class
    :returns: bool -- True if verifield is a (dict||{}||None) with all values of either type required or None; otherwise, False 
    """
    if verifield is None: return True
    if not isinstance(verifield, dict): return False
    all_of = [value or True for value in verifield.values() if isinstance(value, required) or value is None]
    return not verifield or (all(all_of or [False]) and len(all_of) == len(verifield))


dict_type.arg_type = FunctionType
    

def list_type(verifield, required):
    """ Verifies that verifield is an dict type, and either has all values of required type or is an empty object
    
    :param required: Type of all values in a list
    :type required: class
    :returns: bool -- True if verifield is a (list||[]||None) with all values of either type required or None; otherwise, False 
    """
    if verifield is None: return True
    if not isinstance(verifield, list): return False
    all_of = [value or True for value in verifield if isinstance(value, required) or value is None]
    return not verifield or (all(all_of or [False]) and len(all_of) == len(verifield))


list_type.arg_type = FunctionType
    

def min_length(verifield, required):
    """Checks if an (iterable) item meets a minimum length

    :param required: Length the verifield must be
    :param type: int
    :returns: bool -- True if verifield's length is greater or equal to required; otherwise, False
    """
    if verifield is None: return True
    return len(verifield) >= required


min_length.arg_type = int
    

def max_length(verifield, required):
    """Checks if an (iterable) item does not exceed a maximum length

    :param required: Length the verifield must be less than
    :param type: int
    :returns: bool -- True if verifield's length is lesser or equal to required; otherwise, False
    """
    if verifield is None: return True
    return len(verifield) <= required


max_length.arg_type = int
    

def is_type(verifield, required):
    """Checks if an item is of a given type or None

    :param required: The type to verify against
    :type required: class
    :returns: bool -- True if verifield is either the required type or None; otherwise, False
    """
    return verifield is None or isinstance(verifield, required)


is_type.arg_type = FunctionType
    

def url_type(verifield, required):
    """Checks if an item is of a URL pattern

    :param required: Ignored
    :returns: bool -- True if the string passed conforms to URL regex; otherwise, False
    """
    return verifield is None or urlparse(verifield) is not None


url_type.arg_type = int
    

def email_type(verifield, required):
    """Checks if an item is of a email pattern

    :param required: Ignored
    :returns: bool -- True if the string passed conforms to email regex; otherwise, False
    """
    return verifield is None or parseaddr(verifield) != ('','')


email_type.arg_type = int
    

def convert_to(verifield, required):
    """Converts an item to another type

    :param required: Type to convert the item to
    :type required: type
    """
    try:
        verifield = [required(verifi) for verifi in verifield]
        return True
    except:
        return False


convert_to.arg_type = FunctionType
    

def subfields_any(verifield, required):
    """Checks if an item has child dict where any of the fields match the given dict's values

    :param required: Key-values of fields and their values that need to match
    :type required: dict
    :returns: bool -- True if any of the field's values match the required's values
    """
    for req_key, req_val in required.items():
        if getitem(verifield, req_key, '') == req_val:
            return True
    return False


subfields_any.arg_type = dict
    

def subfields_all(verifield, required):
    """ Checks if an item has child dict where ALL of the fields match the given dict's values

    :param required: Key-values of fields and their values that need to match
    :type required: dict
    :returns: bool -- True if all of the fields values match the required's values
    """
    for req_key, req_val in required.items():
        if getitem(verifield, req_key, '') != req_val:
            return False
    return True


subfields_all.arg_type = dict
    

def subfields_none(verifield, required):
    """ Checks if an item has child dict where NONE of the fields match the given dict's values

    :param required: Key-values of fields and their values that need to NOT match
    :type required: dict
    :returns: bool -- True if NONE of the fields values match the required's values
    """
    for req_key, req_val in required.items():
        if getitem(verifield, req_key, '') == req_val:
            return False
    return True


subfields_none.arg_type = dict


def unique_field_value(verifield, unique_to_check):
    """ Checks if an item is already stored in the db with the same tenant, schema, table, field, and value combo
    :param required: Key-values of tenant, schema, table, and field to check the value against
    :returns: bool -- True if the combo does not already exist in the DB
    """
    from polyglot.pyapi.unique import value_combo_exists
    return not value_combo_exists(verifield, **unique_to_check)


class CallableClass:

    def __init__(self, function, additional_info):
        self.function = function
        self.additional_info = additional_info
    
    def __call__(self, *args, **kwargs):
        """Uses things to do stuff"""
        return function(args, addtional_info)


unique_field_value.arg_type = CallableClass
    

def validation_runner(val_funk, field, value, requires):
    """Runs the validation function passed in for a validation.  If the function passes, return an empty dict, else return the field and the validation value it failed with

    :param val_funk: Function that will be called to verify a field value.  Must return a truthy/falsy value
    :type val_funk: func
    :param field: Field name that is being checked, used only for reporting
    :type field: str
    :param requires: Value that is specified as the validation for a value
    :param value: Value of the given field that will be validated
    :returns: dict -- Empty if the validation passed; otherwise, key-value mapping of the field->failure
    """
    if hasattr(requires, '__iter__') and not isinstance(requires, unicode):
        return {field: (val_funk.__name__, requires)} if not val_funk(value, *requires) else {}
    else:
        return {field: (val_funk.__name__, requires)} if not val_funk(value, requires) else {}


def setitem(obj, attr, value):
    """Combination setter for both object and dict types.  Handles the differences between setattr in objects and dict.__setitem__

    :param obj: The target object for setting the value onto
    :type obj: dict | object
    :param attr: The field to be set
    :type attr: str
    :param value: The value to set
    :returns: None
    """
    from functools import partial
    _setattr = partial(setattr, obj)
    setter = getattr(obj, '__setitem__', None) or _setattr
    setter(attr, value)


def getitem(obj, attr, default=None):
    """Combination getter for both object and dict types.  Handles the differences between getattr in objects and dict.__getitem__

    :param obj: The source object to get the value from
    :type obj: dict | object
    :param attr: The field name to get
    :type attr: str
    :param default: The default value to be returned if None is found on the source
    :returns: object -- The value found from the getter
    """
    from functools import partial
    _getattr = partial(getattr, obj)
    getter = getattr(obj, '__getitem__', None) or _getattr
    try:
        return getter(attr)
    except (KeyError, AttributeError):
        return default


def _validate(this, validators):
    """Iterates through a dict of validators and calls the validations on each corresponding field in the 'this' object
    No value will be returned, instead after iteration is complete, if any fields failed validation, they will be added to a dict on the 'this' object called 'validation_errors'.  This will store all failed results returned from the various calls to the validation_runner function.

    :param this: The object that is being validated
    :type this: object
    :param validators: The field->validation function mappings that will be used for validation
    :type validators: dict
    :returns: None
    """
    for val_key, validator in validators.items():
        if isinstance(val_key, tuple):
            field_value, field_name = (getitem(this, val_key[0], None), val_key[0])
            if field_value != val_key[1]:
                continue
            else:
                _validate(this, validator)
                continue
        else:
            field_value, field_name = (getitem(this, val_key, None), val_key)
        if hasattr(field_value, 'validate') and isinstance(validator, dict):
            field_value.validate(validator)
            setitem(this, 'validation_errors', dict(this.validation_errors, **field_value.validation_errors))
        elif isinstance(validator, dict):
            _validate(getitem(this, val_key, None), validator)
        else:
            val_errors = [validation_runner(funkidator[0], field_name, field_value, funkidator[1:]) for funkidator in validator]
            setitem(this, 'validation_errors', dict(getitem(this, 'validation_errors', {}), **dict((key, val) for item in val_errors for key, val in item.items())))


setattr(AppModel, 'validate', _validate)
