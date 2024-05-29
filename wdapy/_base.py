#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Tue Sep 14 2021 15:26:27 by codeskyblue
"""

from http.client import HTTPConnection, HTTPSConnection
import logging
import typing

import json
from retry import retry
from urllib.parse import urlparse

from wdapy._proto import *
from wdapy._types import Recover, StatusInfo
from wdapy.exceptions import *
from wdapy.usbmux.exceptions import MuxConnectError
from wdapy.usbmux.pyusbmux import select_device


logger = logging.getLogger(__name__)

class HTTPResponseWrapper:
    def __init__(self, content: bytes, status_code: int):
        self.content = content
        self.status_code = status_code
    
    def json(self):
        return json.loads(self.content)

    @property
    def text(self) -> str:
        return self.content.decode("utf-8")

    def getcode(self) -> int:
        return self.status_code


def http_create(url: str) -> typing.Union[HTTPConnection, HTTPSConnection]:
    u = urlparse(url)
    if u.scheme == "http+usbmux":
        udid, device_wda_port = u.netloc.split(":")
        device = select_device(udid)
        return device.make_http_connection(int(device_wda_port))
    elif u.scheme == "http":
        return HTTPConnection(u.netloc)
    elif u.scheme == "https":
        return HTTPSConnection(u.netloc)
    else:
        raise ValueError(f"unknown scheme: {u.scheme}")


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
    def _request_http(self, method: RequestMethod, url: str, payload: dict, **kwargs) -> HTTPResponseWrapper:
        """
        Raises:
            RequestError, WDAFatalError
            WDASessionDoesNotExist
        """
        logger.info("request: %s %s %s", method, url, payload)
        try:
            conn = http_create(url)
            conn.timeout = kwargs.get("timeout", self.request_timeout)
            u = urlparse(url)
            urlpath = url[len(u.scheme) + len(u.netloc) + 3:]

            if not payload:
                conn.request(method.value, urlpath)
            else:
                conn.request(method.value, urlpath, json.dumps(payload), headers={"Content-Type": "application/json"})
            response = conn.getresponse()
            content = bytearray()
            while chunk := response.read(4096):
                content.extend(chunk)
            resp = HTTPResponseWrapper(content, response.status)

            if response.getcode() == 200:
                return resp
            else:
                # handle unexpected response
                if "Session does not exist" in resp.text:
                    raise WDASessionDoesNotExist(resp.text)
                else:
                    raise RequestError(f"response code: {response.getcode()}", resp.text)
        except MuxConnectError as err:
            if self._recover:
                if not self._recover.recover():
                    raise WDAFatalError("recover failed")
            raise RequestError("ConnectionBroken", err)

