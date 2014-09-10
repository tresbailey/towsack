def filter_fields(object, fields=()):
    return dict([(key, value) for key, value in object.items() if key not in fields])

