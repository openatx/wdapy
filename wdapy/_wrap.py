# coding: utf-8
#

import typing


class Wrapper:
    """
    MetaClass ref:
        https://www.jianshu.com/p/224ffcb8e73e
    """

    def __init__(self):
        self._request_timeout = None


def timeout(seconds: typing.Union[float, int]):
    def _timeout_wrapper(fn):
        def _inner(self, *args, **kwargs):
            old_timeout = self._request_timeout
            try:
                return fn(self, *args, **kwargs)
            finally:
                self._request_timeout = old_timeout
        return _inner
    return _timeout_wrapper
