# coding: utf-8

import abc
import base64
import enum
import functools
import io
import json
import typing

from logzero import setup_logger
import requests
from cached_property import cached_property
from PIL import Image

from ._proto import *
from ._types import *
from .exceptions import *

logger = setup_logger("wdapy")


class HTTPResponse:
    def __init__(self, resp: requests.Response, err: requests.RequestException):
        self._resp = resp
        self._err = err

    def is_success(self) -> bool:
        return self._err is None and self._resp.status_code == 200

    def json(self) -> dict:
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


class CommonClient(abc.ABC):
    def __init__(self, wda_url: str):
        self._wda_url = wda_url
        self._request_timeout = None

        self._session_id: str = None
        self._recover: Recover = None
        self.__ui_size = None

    def app_start(self, bundle_id: str):
        self.session_request(POST, "/wda/apps/launch", {
            "bundleId": bundle_id
        })

    def app_terminate(self, bundle_id: str):
        self.session_request(POST, "/wda/apps/terminate", {
            "bundleId": bundle_id
        })

    def app_state(self, bundle_id: str) -> AppState:
        value = self.session_request(POST, "/wda/apps/state", {
            "bundleId": bundle_id
        })["value"]
        return AppState(value)

    def app_current(self) -> AppInfo:
        self.unlock()
        st = self.status()
        if st.session_id is None:
            self.session()
        data = self.request(GET, "/wda/activeAppInfo")
        value = data['value']
        return AppInfo.value_of(value)

    def sourcetree(self) -> SourceTree:
        data = self.request(GET, "/source")
        return SourceTree.value_of(data)

    def status(self) -> StatusInfo:
        data = self.request(GET, "/status")
        return StatusInfo.value_of(data)

    def open_url(self, url: str):
        self.session_request(POST, "/url", {
            "url": url
        })

    def appium_settings(self, kwargs: dict = None) -> dict:
        if kwargs is None:
            return self.session_request(GET, "/appium/settings")["value"]
        payload = {"settings": kwargs}
        return self.session_request(POST, "/appium/settings", payload)["value"]

    def is_locked(self) -> bool:
        return self.request(GET, "/wda/locked")["value"]

    def unlock(self):
        self.request(POST, "/wda/unlock")

    def lock(self):
        self.request(POST, "/wda/lock")

    def homescreen(self):
        self.request(POST, "/wda/homescreen")

    def shutdown(self):
        self.request(GET, "/wda/shutdown")

    def get_orientation(self) -> Orientation:
        value = self.session_request(GET, '/orientation')['value']
        return Orientation(value)

    def window_size(self) -> typing.Tuple[int, int]:
        """
        Returns:
            UISize
        """
        # 这里做了一点速度优化，跟进图像大小获取屏幕尺寸
        orientation = self.get_orientation()
        if self.__ui_size is None:
            # 这里认为screenshot返回的屏幕转向时正确的
            pixel_width, pixel_height = self.screenshot().size
            w, h = pixel_width//self.scale, pixel_height//self.scale
            if self.get_orientation() == Orientation.PORTRAIT:
                self.__ui_size = (w, h)
            else:
                self.__ui_size = (h, w)

        if orientation == Orientation.LANDSCAPE:
            return self.__ui_size[::-1]
        else:
            return self.__ui_size

    def tap(self, x: int, y: int):
        self.session_request(POST, "/wda/tap/0", {"x": x, "y": y})

    def swipe(self,
              from_x: int,
              from_y: int,
              to_x: int,
              to_y: int,
              duration: float = 0.2):
        payload = {
            "fromX": from_x,
            "fromY": from_y,
            "toX": to_x,
            "toY": to_y,
            "duration": duration}
        self.session_request(POST, "/wda/dragfromtoforduration", payload)

    @cached_property
    def scale(self) -> int:
        # Response example
        # {"statusBarSize": {'width': 320, 'height': 20}, 'scale': 2}
        value = self.session_request(GET, "/wda/screen")['value']
        return value['scale']

    @cached_property
    def status_barsize(self) -> int:
        # Response example
        # {"statusBarSize": {'width': 320, 'height': 20}, 'scale': 2}
        value = self.session_request(GET, "/wda/screen")['value']
        return value['statusBarSize']

    def screenshot(self) -> Image.Image:
        """ take screenshot """
        value = self.request(GET, "/screenshot")["value"]
        raw_value = base64.b64decode(value)
        buf = io.BytesIO(raw_value)
        im = Image.open(buf)
        return im.convert("RGB")

    def battery_info(self):
        data = self.session_request(GET, "/wda/batteryInfo")["value"]
        return BatteryInfo.value_of(data)

    def device_info(self):
        data = self.session_request(GET, "/wda/device/info")["value"]
        return DeviceInfo.value_of(data)

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
        session_id = self._get_valid_session_id()
        urlpath = f"/session/{session_id}/" + urlpath.lstrip("/")
        return self.request(method, urlpath, payload)

    def request(self, method: RequestMethod, urlpath: str, payload: dict = None) -> dict:
        full_url = self._wda_url.rstrip("/") + "/" + urlpath.lstrip("/")
        logger.debug("$ %s", f"curl -X{method} {full_url} -d {payload!r}")
        resp = self._request_with_error(method, full_url, payload)
        if not resp.is_success():
            if self._recover and not self._recover.recover():
                raise RequestError(
                    "recover failed", resp.get_error_message())
            resp = self._request_with_error(method, full_url, payload)

        short_json = resp.json().copy()
        for k, v in short_json.items():
            if isinstance(v, str) and len(v) > 40:
                v = v[:20] + "... skip ..." + v[-10:]
            short_json[k] = v
        logger.debug("==> Response <==\n%s", json.dumps(short_json, indent=4))

        value = resp.json().get("value")
        if value and isinstance(value, dict) and value.get("error"):
            raise ApiError(value["error"], value.get("message"))

        return resp.json()

    def _request_with_error(self, method: RequestMethod, url: str, payload: dict, **kwargs) -> HTTPResponse:
        _request = functools.partial(
            requests.request, method, url, json=payload)
        try:
            resp = _request(**kwargs)
            return HTTPResponse(resp, None)
        except requests.RequestException as err:
            return HTTPResponse(err.response, err)


class AppiumClient(CommonClient):
    """
    client for https://github.com/appium/WebDriverAgent
    """

    def __init__(self, wda_url: str = DEFAULT_WDA_URL):
        super().__init__(wda_url)


class NanoscopicClient(AppiumClient):
    """
    Repo: https://github.com/nanoscopic/WebDriverAgent

    This repo changes a lot recently and the new version code drop the HTTP API to NNG
    So here use the old commit version
    https://github.com/nanoscopic/WebDriverAgent/tree/d07372d73a4cc4dc0b0d7807271e6d7958e57302
    """

    def tap(self, x: int, y: int):
        """ fast tap """
        self.request(POST, "/wda/tap", {
            "x": x,
            "y": y,
        })

    def swipe(self,
              from_x: int,
              from_y: int,
              to_x: int,
              to_y: int,
              duration: float = .2):
        """ fast swipe """
        self.request(POST, "/wda/swipe", {
            "x1": from_x,
            "y1": from_y,
            "x2": to_x,
            "y2": to_y,
            "delay": duration})
