from exception.ValidateException import ValidateException
def valiate_require(data, need=[]):
    if not isinstance(need, list):
        raise ValidateException('require validate need a list')
    for field in need:
        if not (field in data):
            raise ValidateException(field + ' is required')
def fill_default_fields(data, fields=[], default=""):
    if not isinstance(fields, list):
        raise ValidateException('full default fields need a list')
    for field in fields:
        if not (field in data):
            data[field] = default
    return data

