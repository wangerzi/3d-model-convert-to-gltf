from exception.ValidateException import ValidateException
from aiohttp import web
import re

def valiate_require(data, need=[]):
    for field in need:
        if not data.has_key(field):
            raise ValidateException(field + 'is required')

def validate_file(field):
    if not isinstance(field, web.FileField):
        raise ValidateException('file field must be File')
def validate_callback(field):
    if not isinstance(field, str):
        raise ValidateException('callback field must be string')
    # em...,maybe need to check url
    regex = re.compile(r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?')
    if re.search(regex, field):
        raise ValidateException('callback field must be url format')
def validate_req_id(field):
    if not isinstance(field, int):
        raise ValidateException('callback field must be int')
def validate_customize_data(field):
    if not isinstance(field, str):
        raise ValidateException('customize_data field must be string')

def stl(request, data):
    validate_file(data['file'])
    validate_callback(data['callback'])
    validate_customize_data(data['customize_data'])
def stp(request, data):
    validate_file(data['file'])
    validate_callback(data['callback'])
    validate_customize_data(data['customize_data'])
def iges(request, data):
    validate_file(data['file'])
    validate_callback(data['callback'])
    validate_customize_data(data['customize_data'])
def process(request, data):
    validate_req_id(data['req_id'])
