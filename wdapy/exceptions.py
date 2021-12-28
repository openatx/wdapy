# coding: utf-8
#

class WDAException(Exception):
    pass


class RequestError(WDAException):
    pass


class WDASessionDoesNotExist(WDAException):
    """ Session does not exist """


class ApiError(WDAException):
    def __init__(self, error: str, message: str):
        self.error = error
        self.message = message
