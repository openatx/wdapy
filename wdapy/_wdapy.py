# coding: utf-8

import atexit
import base64
import io
import json
import logging
import queue
import subprocess
import sys
import threading
import time
import typing

import requests
from cached_property import cached_property
from logzero import setup_logger
from PIL import Image

from ._alert import Alert
from ._base import BaseClient
from ._logger import logger
from ._proto import *
from ._types import *
from .exceptions import *
from .usbmux import requests_usbmux, usbmux


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
        if self._resp:
            return self._resp.text
        return str(self._err)

    def raise_if_failed(self):
        if self._err:
            raise RequestError("HTTP request error", self._err)
        if self._resp.status_code != 200:
            raise RequestError(self._resp.status_code, self._resp.text)


class CommonClient(BaseClient):
    def __init__(self, wda_url: str):
        super().__init__(wda_url)
        self.__ui_size = None
        self.__debug = False

    @property
    def debug(self) -> bool:
        return self.__debug

    @debug.setter
    def debug(self, v: bool):
        if v:
            setup_logger(NAME)
        else:
            setup_logger(NAME, level=logging.INFO)

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

    def app_list(self) -> AppList:
        value = self.session_request(GET, "/wda/apps/list")["value"][0]
        return AppList.value_of(value)

    def deactivate(self, duration: float):
        self.session_request(POST, "/wda/deactivateApp", {
            "duration": duration
        })

    @cached_property
    def alert(self) -> Alert:
        return Alert(self)

    def sourcetree(self) -> SourceTree:
        data = self.request(GET, "/source")
        return SourceTree.value_of(data)

    def open_url(self, url: str):
        self.session_request(POST, "/url", {
            "url": url
        })

    def set_clipboard(self, content: str, content_type="plaintext"):
        """ only works when WDA app is foreground """
        self.session_request(POST, "/wda/setPasteboard",{
            "content": base64.b64encode(content.encode()).decode(),
            "contentType": content_type
        })
    
    def get_clipboard(self, content_type="plaintext") -> str:
        data = self.session_request(POST, "/wda/getPasteboard",{
            "contentType": content_type
        })
        return base64.b64decode(data['value']).decode('utf-8')

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
        
        Ref:
            FBElementCommands.m
        """
        data = self.session_request(GET, "/window/size")
        return data['value']['width'], data['value']['height']
        
        # 代码暂时保留，下面的方法为通过截图获取屏幕大小
        # # 这里做了一点速度优化，跟进图像大小获取屏幕尺寸
        # orientation = self.get_orientation()
        # if self.__ui_size is None:
        #     # 这里认为screenshot返回的屏幕转向时正确的
        #     pixel_width, pixel_height = self.screenshot().size
        #     w, h = pixel_width//self.scale, pixel_height//self.scale
        #     if self.get_orientation() == Orientation.PORTRAIT:
        #         self.__ui_size = (w, h)
        #     else:
        #         self.__ui_size = (h, w)

        # if orientation == Orientation.LANDSCAPE:
        #     return self.__ui_size[::-1]
        # else:
        #     return self.__ui_size

    def send_keys(self, value: str):
        """ input with some text """
        self.session_request(POST, "/wda/keys", {"value": list(value)})

    def tap(self, x: int, y: int):
        self.session_request(POST, "/wda/tap/0", {"x": x, "y": y})
    
    def touch_and_hold(self, x: int, y: int, duration: float):
        """ touch and hold
        
        Ref:
            FBElementCommands.m
        """
        self.session_request(POST, "/wda/touchAndHold", {"x": x, "y": y, "duration": duration})

    def swipe(self,
              from_x: int,
              from_y: int,
              to_x: int,
              to_y: int,
              duration: float = 0.5):
        payload = {
            "fromX": from_x,
            "fromY": from_y,
            "toX": to_x,
            "toY": to_y,
            "duration": duration}
        self.session_request(POST, "/wda/dragfromtoforduration", payload)

    def press(self, name: Keycode):
        payload = {
            "name": name
        }
        self.session_request(POST, "/wda/pressButton", payload)

    def press_duration(self, name: Keycode, duration: float):
        hid_usages = {
            "home": 0x40,
            "volumeup": 0xE9,
            "volumedown": 0xEA,
            "power": 0x30,
            "snapshot": 0x65,
            "power_plus_home": 0x65
        }
        name = name.lower()
        if name not in hid_usages:
            raise ValueError("Invalid name:", name)
        hid_usages = hid_usages[name]
        payload = {
            "page": 0x0C,
            "usage": hid_usages,
            "duration": duration
        }
        return self.session_request(POST, "/wda/performIoHidEvent", payload)

    @cached_property
    def scale(self) -> int:
        # Response example
        # {"statusBarSize": {'width': 320, 'height': 20}, 'scale': 2}
        value = self.session_request(GET, "/wda/screen")['value']
        return value['scale']

    def status_barsize(self) -> StatusBarSize:
        # Response example
        # {"statusBarSize": {'width': 320, 'height': 20}, 'scale': 2}
        value = self.session_request(GET, "/wda/screen")['value']
        return StatusBarSize.value_of(value['statusBarSize'])

    def screenshot(self) -> Image.Image:
        """ take screenshot """
        value = self.request(GET, "/screenshot")["value"]
        raw_value = base64.b64decode(value)
        buf = io.BytesIO(raw_value)
        im = Image.open(buf)
        return im.convert("RGB")

    def battery_info(self) -> BatteryInfo:
        data = self.session_request(GET, "/wda/batteryInfo")["value"]
        return BatteryInfo.value_of(data)

    @property
    def info(self) -> DeviceInfo:
        return self.device_info()

    def device_info(self) -> DeviceInfo:
        data = self.session_request(GET, "/wda/device/info")["value"]
        return DeviceInfo.value_of(data)



class XCUITestRecover(Recover):
    def __init__(self, udid: str):
        self._udid = udid

    def recover(self) -> bool:
        """ launch by tidevice
        
        https://github.com/alibaba/tidevice
        """
        logger.info("WDA is starting using tidevice ...")
        args = [sys.executable, '-m', 'tidevice', '-u', self._udid, 'xctest']
        p = subprocess.Popen(args,
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         start_new_session=True,
                         close_fds=True, encoding="utf-8")
        
        que = queue.Queue()
        threading.Thread(target=self.drain_process_output, args=(p, que), daemon=True).start()
        try:
            success = que.get(timeout=20)
            return success
        except queue.Empty:
            logger.warning("WDA launch timeout 20s")
            p.kill()
            return False

    def drain_process_output(self, p: subprocess.Popen, msg_queue: queue.Queue):
        deadline = time.time() + 10
        lines = []
        while time.time() < deadline:
            if p.poll() is not None:
                logger.warning("xctest exited, output --.\n %s", "\n".join(lines)) # p.stdout.read())
                msg_queue.put(False)
                return
            line = p.stdout.readline().strip()
            lines.append(line)
            # logger.info("%s", line)
            if "WebDriverAgent start successfully" in line:
                logger.info("WDA started")
                msg_queue.put(True)
                break
        
        atexit.register(p.terminate)
        while p.stdout.read() != "":
            pass


class AppiumClient(CommonClient):
    """
    client for https://github.com/appium/WebDriverAgent
    """

    def __init__(self, wda_url: str = DEFAULT_WDA_URL):
        super().__init__(wda_url)


class AppiumUSBClient(AppiumClient):
    def __init__(self, udid: str = None, port: int = 8100):
        if udid is None:
            _usbmux = usbmux.Usbmux()
            udid = _usbmux.get_single_device_udid()
        super().__init__(requests_usbmux.DEFAULT_SCHEME+udid+f":{port}")
        self.set_recover_handler(XCUITestRecover(udid))


class NanoClient(AppiumClient):
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
              duration: float = .5):
        """ fast swipe """
        self.request(POST, "/wda/swipe", {
            "x1": from_x,
            "y1": from_y,
            "x2": to_x,
            "y2": to_y,
            "delay": duration})


class NanoUSBClient(NanoClient):
    def __init__(self, udid: str = None, port: int = 8100):
        if udid is None:
            _usbmux = usbmux.Usbmux()
            udid = _usbmux.get_single_device_udid()
        super().__init__(requests_usbmux.DEFAULT_SCHEME+udid+f":{port}")
        self.set_recover_handler(XCUITestRecover(udid))
