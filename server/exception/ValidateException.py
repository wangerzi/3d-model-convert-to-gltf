from exception.BaseException import BaseException

class ValidateException(BaseException):
    def __init__(self, err="Validate error"):
        BaseException.__init__(self, err)
