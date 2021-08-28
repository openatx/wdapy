# coding: utf-8

import abc
import enum

import requests
from PIL import Image

from ._proto import *
from ._types import *


class CommonClient(abc.ABC):
    _recover = None
    _session_id = None

    def __init__(self, wda_url: str):
        self._wda_url = wda_url

    def app_start(self):
        pass

    def app_terminate(self):
        pass

    def app_current(self):
        self.unlock()
        raise NotImplementedError()

    def status(self) -> StatusInfo:
        data = self.request(GET, "/status")
        return StatusInfo.value_of(data)

    @property
    def info(self) -> DeviceInfo:
        pass

    def lock(self):
        pass

    def unlock(self):
        pass

    def window_size(self) -> WindowSize:
        pass

    def click(self, x: int, y: int):
        pass

    def swipe(self, from_x: int, from_y: int, to_x: int, to_y: int):
        pass

    def scale(self) -> int:
        pass

    def screenshot(self) -> Image.Image:
        pass

    @property
    def locked(self) -> bool:
        raise NotImplementedError()

    def session(self, bundle_id: str = None) -> str:
        st = self.status()
        if st.session_id:
            return st.session_id
        resp = self.request(POST, "/session", {"direcpp": ""})  # TODO
        return

    def set_recover_handler(self, recover: Recover):
        self._recover = Recover

    def session_request(self, method: RequestMethod, urlpath: str, payload: dict = None) -> dict:
        session_id = self.session()
        urlpath = f"/session/{session_id}/" + urlpath.lstrip("/")
        return self.request(method, urlpath, payload)

    def request(self, method: RequestMethod, urlpath: str, payload: dict = None) -> dict:
        full_url = self._wda_url.rstrip("/") + "/" + urlpath.lstrip("/")
        resp = requests.request(method.value, full_url, json=payload)
        return resp.json()


class AppiumClient(CommonClient):
    """
    client for https://github.com/appium/WebDriverAgent
    """

    def __init__(self, wda_url: str = DEFAULT_WDA_URL):
        super().__init__(wda_url)


class MyClient(AppiumClient):
    pass
