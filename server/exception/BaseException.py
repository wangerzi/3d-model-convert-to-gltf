class BaseException(Exception):
    def __init__(self, err="Program exec error"):
        Exception.__init__(self, err)
