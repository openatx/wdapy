#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Tue Sep 14 2021 15:26:27 by codeskyblue
"""

import functools
import typing

import requests
import simplejson as json

from ._logger import logger
from ._proto import *
from ._types import Recover, StatusInfo
from .exceptions import *
from .usbmux import MuxError, requests_usbmux


class HTTPResponse:
    def __init__(self, resp: requests.Response, err: requests.RequestException):
        self._response: requests.Response = resp
        self._error: typing.Optional[Exception] = err

    @property
    def status_code(self) -> int:
        if self._response is None:
            return None
        return self._response.status_code

    def is_success(self) -> bool:
        return self._error is None and self.status_code == 200
    
    def raise_if_session_error(self):
        """
        Raises:
            WDASessionDoesNotExist
        """
        if self._error and "Session does not exist" in str(self._error):
            raise WDASessionDoesNotExist(self._error)

    def should_call_recover(self) -> bool:
        """
        Only return true when WDA is no response or can not connected
        """
        if isinstance(self._error, MuxError):
            return True
        elif self.status_code is None:
            return True
        return False
        
    def json(self) -> dict:
        assert self._response is not None
        try:
            return self._response.json()
        except json.JSONDecodeError:
            return RequestError("JSON decode error", self._response.text)

    def get_error_message(self) -> str:
        if self._response is not None:
            message = self._response.text
        else:
            message = f"{self._error}"
        return f"{message} status_code:{self.status_code}"

    def raise_if_failed(self):
        if self._error:
            raise RequestError("HTTP request error", self._error)
        if self.status_code != 200:
            raise RequestError(self.status_code, self._response.text)


class BaseClient:
    def __init__(self, wda_url: str):
        self._wda_url = wda_url.rstrip("/") + "/"

        self._session_id: str = None
        self._recover: Recover = None

        self.__request_timeout = DEFAULT_HTTP_TIMEOUT
    
    @property
    def request_timeout(self) -> float:
        return self.__request_timeout
    
    @request_timeout.setter
    def request_timeout(self, timeout: float):
        self.__request_timeout = timeout

    def status(self) -> StatusInfo:
        data = self.request(GET, "/status")
        return StatusInfo.value_of(data)

    def session(self,
                bundle_id: str = None,
                arguments: list = None,
                environment: dict = None) -> str:
        """ create session and return session id """
        capabilities = {}
        if bundle_id:
            always_match = {
                "bundleId": bundle_id,
                "arguments": arguments or [],
                "environment": environment or {},
                "shouldWaitForQuiescence": False,
            }
            capabilities['alwaysMatch'] = always_match
        payload = {
            "capabilities": capabilities,
            "desiredCapabilities": capabilities.get('alwaysMatch',
                                                    {}),  # 兼容旧版的wda
        }
        data = self.request(POST, "/session", payload)

        # update cached session_id
        self._session_id = data['sessionId']
        return self._session_id

    def set_recover_handler(self, recover: Recover):
        self._recover = recover

    def _get_valid_session_id(self) -> str:
        if self._session_id:
            return self._session_id
        old_session_id = self.status().session_id
        if old_session_id:
            self._session_id = old_session_id
        else:
            self._session_id = self.session()
        return self._session_id

    def session_request(self, method: RequestMethod, urlpath: str, payload: dict = None) -> dict:
        """ request with session_id """
        session_id = self._get_valid_session_id()
        session_urlpath = f"/session/{session_id}/" + urlpath.lstrip("/")
        try:
            return self.request(method, session_urlpath, payload)
        except WDASessionDoesNotExist:
            # In some condition, session_id exist in /status, but not working
            # The bellow code fix that case
            logger.info("session %r does not exist, generate new one", session_id)
            session_id = self._session_id = self.session()
            session_urlpath = f"/session/{session_id}/" + urlpath.lstrip("/")
            return self.request(method, session_urlpath, payload)

    def request(self, method: RequestMethod, urlpath: str, payload: dict = None) -> dict:
        """
        """
        full_url = self._wda_url.rstrip("/") + "/" + urlpath.lstrip("/")
        payload_debug = payload or ""
        logger.debug("$ %s", f"curl -X{method} --max-time {self.request_timeout:d} {full_url} -d {payload_debug!r}")
        
        resp = self._request_with_error(method, full_url, payload)
        resp.raise_if_session_error()

        if resp.should_call_recover():
            if self._recover:
                if not self._recover.recover():
                    raise RequestError(
                        "recover failed", resp.get_error_message())
            resp = self._request_with_error(method, full_url, payload)
        resp.raise_if_failed()

        short_json = resp.json().copy()
        for k, v in short_json.items():
            if isinstance(v, str) and len(v) > 40:
                v = v[:20] + "... skip ..." + v[-10:]
            short_json[k] = v
        logger.debug("==> Response <==\n%s", json.dumps(short_json, indent=4, ensure_ascii=False))

        value = resp.json().get("value")
        if value and isinstance(value, dict) and value.get("error"):
            raise ApiError(value["error"], value.get("message"))

        return resp.json()

    def _request_with_error(self, method: RequestMethod, url: str, payload: dict, **kwargs) -> HTTPResponse:
        session = self._requests_session_pool_get()
        _request = functools.partial(
            session.request, method, url, json=payload, timeout=self.request_timeout)
        try:
            resp = _request(**kwargs)
            return HTTPResponse(resp, None)
        except requests.RequestException as err:
            return HTTPResponse(err.response, err)
        except MuxError as err:
            return HTTPResponse(requests.Response(), err)

    @functools.lru_cache(1024)
    def _requests_session_pool_get(self) -> requests.Session:
        return requests_usbmux.Session()

