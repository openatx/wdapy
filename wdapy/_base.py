#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Tue Sep 14 2021 15:26:27 by codeskyblue
"""

import functools
import logging
import typing

import requests
import simplejson as json
from retry import retry

from wdapy._logger import logger
from wdapy._proto import *
from wdapy._types import Recover, StatusInfo
from wdapy.exceptions import *
from wdapy.usbmux import MuxError, requests_usbmux


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
        Raises:
            RequestError, WDASessionDoesNotExist
        """
        full_url = self._wda_url.rstrip("/") + "/" + urlpath.lstrip("/")
        payload_debug = payload or ""
        logger.debug("$ %s", f"curl -X{method} --max-time {self.request_timeout:d} {full_url} -d {payload_debug!r}")
        
        resp = self._request_http(method, full_url, payload)
        try:
            short_json = resp.json().copy()
        except json.JSONDecodeError:
            raise RequestError("response is not json format", resp.text)

        for k, v in short_json.items():
            if isinstance(v, str) and len(v) > 40:
                v = v[:20] + "... skip ..." + v[-10:]
            short_json[k] = v
        logger.debug("==> Response <==\n%s", json.dumps(short_json, indent=4, ensure_ascii=False))

        value = resp.json().get("value")
        if value and isinstance(value, dict) and value.get("error"):
            raise ApiError(resp.status_code, value["error"], value.get("message"))

        return resp.json()

    @retry(RequestError, tries=2, delay=0.2, jitter=0.1, logger=logging)
    def _request_http(self, method: RequestMethod, url: str, payload: dict, **kwargs) -> requests.Response:
        """
        Raises:
            RequestError, WDAFatalError
            WDASessionDoesNotExist
        """
        session = self._requests_session_pool_get()
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.request_timeout
        try:
            resp = session.request(method, url, json=payload, timeout=self.request_timeout)
            if resp.status_code == 200:
                return resp
            else:
                # handle unexpected response
                if "Session does not exist" in resp.text:
                    raise WDASessionDoesNotExist(resp.text)
                else:
                    raise RequestError(resp.text)
        except (requests.RequestException, MuxError) as err:
            if self._recover:
                if not self._recover.recover():
                    raise WDAFatalError("recover failed", err)
            raise RequestError("ConnectionBroken", err)

    @functools.lru_cache(1024)
    def _requests_session_pool_get(self) -> requests.Session:
        return requests_usbmux.Session()

