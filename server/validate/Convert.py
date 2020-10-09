from exception.ValidateException import ValidateException
import validate.Base as Base
from aiohttp import web
import re


def validate_file(field):
    if not isinstance(field, web.FileField):
        raise ValidateException('file field must be File')


def validate_callback(field):
    if not isinstance(field, str):
        raise ValidateException('callback field must be string')
    # em...,maybe need check url format
    regex = re.compile(r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?')
    if re.search(regex, field):
        raise ValidateException('callback field must be url format')


def validate_req_id(field):
    if not isinstance(field, str):
        raise ValidateException('req_id field must be str')


def validate_customize_data(field):
    if not isinstance(field, str):
        raise ValidateException('customize_data field must be string')


def stl(request, data):
    Base.valiate_require(data, ['file'])

    validate_file(data['file'])


def stp(request, data):
    Base.valiate_require(data, ['file'])

    validate_file(data['file'])


def iges(request, data):
    Base.valiate_require(data, ['file'])

    validate_file(data['file'])


def obj(request, data):
    Base.valiate_require(data, ['file'])

    validate_file(data['file'])


def fbx(request, data):
    Base.valiate_require(data, ['file'])

    validate_file(data['file'])
