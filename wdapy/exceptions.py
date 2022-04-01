# coding: utf-8
#

class WDAException(Exception):
    pass


class RequestError(WDAException):
    pass


class WDASessionDoesNotExist(WDAException):
    """ Session does not exist """


class ApiError(RequestError):
    """ request error, but with formated data """


class WDAFatalError(RequestError):
    """ unrecoverable error """