from exception.BaseException import BaseException

class ConvertException(BaseException):
    def __init__(self, err="Convert error"):
        BaseException.__init__(self, err)
