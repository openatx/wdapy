#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Tue Sep 14 2021 15:26:27 by codeskyblue
"""

import functools

import requests
import simplejson as json

from ._proto import *
from ._types import Recover, StatusInfo
from .exceptions import *
from .usbmux import requests_usbmux


class HTTPResponse:
    def __init__(self, resp: requests.Response, err: requests.RequestException):
        self._resp = resp
        self._err = err

    def is_success(self) -> bool:
        return self._err is None and self._resp.status_code == 200

    def json(self) -> dict:
        assert self._resp is not None
        try:
            return self._resp.json()
        except json.JSONDecodeError:
            return RequestError("JSON decode error", self._resp.text)

    def get_error_message(self) -> str:
        # if self._err:
        #     return str(self._err)
        # self.json()
        if self._resp:
            return self._resp.text
        return str(self._err)

    def raise_if_failed(self):
        if self._err:
            raise RequestError("HTTP request error", self._err)
        if self._resp.status_code != 200:
            raise RequestError(self._resp.status_code, self._resp.text)



class BaseClient:
    def __init__(self, wda_url: str):
        self._wda_url = wda_url
        self._request_timeout = None

        self._session_id: str = None
        self._recover: Recover = None
    
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
        self._recover = Recover

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
        urlpath = f"/session/{session_id}/" + urlpath.lstrip("/")
        try:
            return self.request(method, urlpath, payload)
        except RequestError as e:
            # In some condition, session_id exist in /status, but not working
            # The bellow code fix that case
            if len(e.args) >= 2 and "Session does not exist" in e.args[1]:
                self._session_id = self.session()
                urlpath = f"/session/{session_id}/" + urlpath.lstrip("/")
                return self.request(method, urlpath, payload)
            raise
            

    def request(self, method: RequestMethod, urlpath: str, payload: dict = None) -> dict:
        """
        """
        full_url = self._wda_url.rstrip("/") + "/" + urlpath.lstrip("/")
        payload_debug = payload or ""
        logger.debug("$ %s", f"curl -X{method} {full_url} -d {payload_debug!r}")
        
        resp = self._request_with_error(method, full_url, payload)
        if not resp.is_success():
            if self._recover and not self._recover.recover():
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
            session.request, method, url, json=payload)
        try:
            resp = _request(**kwargs)
            return HTTPResponse(resp, None)
        except requests.RequestException as err:
            return HTTPResponse(err.response, err)

    @functools.lru_cache(1024)
    def _requests_session_pool_get(self) -> requests.Session:
        return requests_usbmux.Session()

