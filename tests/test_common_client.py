# coding: utf-8
#

import unittest
from unittest.mock import MagicMock
import wdapy
from wdapy import AppiumClient
from wdapy._types import BatteryState, Gesture, GestureAction


class SimpleTest(unittest.TestCase):
    def setUp(self):
        self._client = AppiumClient("http://localhost:8100")

    def test_status(self):
        self._client.request = MagicMock(return_value={
            "sessionId": "yyds",
            "value": {
                "message": "WebDriverAgent is ready to accept commands",
                "ios": {
                    "ip": "1.2.3.4",
                }
            }
        })
        st = self._client.status()
        self.assertEqual("1.2.3.4", st.ip)
        self.assertEqual("yyds", st.session_id)
        self.assertEqual(
            "WebDriverAgent is ready to accept commands", st.message)

    def test_sourcetree(self):
        self._client.request = MagicMock(return_value={
            "value": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n",
            "sessionId": "test"
        })
        sourcetree = self._client.sourcetree()
        self.assertEqual("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n", sourcetree.value)


    def test_is_locked(self):
        m = MagicMock(return_value={
            "value": False,
        })
        self._client.request = m
        self.assertEqual(False, self._client.is_locked())

    def test_app_start(self):
        pass

    def test_app_terminate(self):
        pass

    def test_unlock(self):
        pass

    def test_deviceinfo(self):
        self._client.session_request = MagicMock(return_value={
            "value": {
                "timeZone": "GMT+0800",
                "currentLocale": "zh_CN",
                "model": "iPhone",
                "uuid": "12345678-ABCD-1234-ABCD-123456789ABC",
                "userInterfaceIdiom": 0,
                "userInterfaceStyle": "light",
                "name": "iPhone X",
                "isSimulator": False
            }
        })
        di = self._client.device_info()
        self.assertEqual("GMT+0800", di.time_zone)
        self.assertEqual("zh_CN", di.current_locale)
        self.assertEqual("iPhone", di.model)
        self.assertEqual("12345678-ABCD-1234-ABCD-123456789ABC", di.uuid)
        self.assertEqual(0, di.user_interface_idiom)
        self.assertEqual("light", di.user_interface_style)
        self.assertEqual("iPhone X", di.name)
        self.assertEqual(False, di.is_simulator)

    def test_orientation(self):
        self._client.session_request = MagicMock(return_value={
            "value": "PORTRAIT"
        })
        ot = self._client.get_orientation()
        self.assertEqual("PORTRAIT", ot)

    def test_batteryinfo(self):
        self._client.session_request = MagicMock(return_value={
            "value": {
                "level": 0.9999999999999999,
                "state": 0
            }
        })
        bi = self._client.battery_info()
        self.assertEqual(0.9999999999999999, bi.level)
        self.assertEqual(0, bi.state)
        self.assertIn(bi.state, BatteryState)

    def test_statusbarsize(self):
        self._client.session_request = MagicMock(return_value={
            "value": {
                "statusBarSize": {
                    "width": 320,
                    "height": 20
                }
            }
        })
        sts = self._client.status_barsize()
        self.assertEqual(320, sts.width)
        self.assertEqual(20, sts.height)

    def test_applist(self):
        self._client.session_request = MagicMock(return_value={
            "value": {
                "AppList": {
                    "pid": 4453,
                    "bundle_id": "com.apple.springboard"
                }
            }
        })
        with self.assertRaises(KeyError):
            al = self._client.app_list()
            self.assertEqual(4453, al.pid)
            self.assertEqual("com.apple.springboard", al.bundle_id)

    def test_press(self):
        self._client.session_request = MagicMock(return_value={"value": None})
        self._client.press(wdapy.Keycode.HOME)
        payload = self._client.session_request.call_args.args[-1]
        self.assertEqual(wdapy.Keycode.HOME, payload['name'])
    
    def test_keyboard_dismiss(self):
        self._client.session_request = MagicMock(return_value={"value": None})
        self._client.keyboard_dismiss(["Done"])
        payload = self._client.session_request.call_args.args[-1]
        self.assertEqual(["Done"], payload['keyNames'])

    def test_touch_perform(self):
        self._client.session_request = MagicMock(return_value={"value": None})
        gestures = [
            Gesture(GestureAction.TAP, options={"x": 100, "y": 200})
        ]
        self._client.touch_perform([{"action": "tap", "options": {"x": 100, "y": 200}}])
        payload = self._client.session_request.call_args.args[-1]
        self.assertEqual([{"action": "tap", "options": {"x": 100, "y": 200}}], payload['actions'])


if __name__ == "__main__":
    unittest.main()
