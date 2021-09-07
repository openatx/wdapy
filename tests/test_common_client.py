# coding: utf-8
#

import unittest
from unittest.mock import MagicMock
from wdapy import AppiumClient


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
        self.assertEqual("test", sourcetree.sessionId)


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
            "timeZone": "GMT+0800",
            "currentLocale": "zh_CN",
            "model": "iPhone",
            "uuid": "12345678-ABCD-1234-ABCD-123456789ABC",
            "userInterfaceIdiom": 0,
            "userInterfaceStyle": "light",
            "name": "iPhone X",
            "isSimulator": False
        })
        di = self._client.device_info()
        self.assertEqual("GMT+0800", di.time_zone)
        self.assertEqual("zh_CN", di.current_locale)
        self.assertEqual("iPhone", di.model)
        self.assertEqual("12345678-ABCD-1234-ABCD-123456789ABC", di.uuid)
        self.assertEqual(0, di.userinterface_idiom)
        self.assertEqual("light", di.userinterface_style)
        self.assertEqual("iPhone X", di.name)
        self.assertEqual(False, di.is_simulator)

    def test_batteryinfo(self):
        self._client.session_request = MagicMock(return_value={
            "level": 0.9999999999999999,
            "state": 2
        })
        bi = self._client.battery_info()
        self.assertEqual(0.9999999999999999, bi.level)
        self.assertEqual(2, bi.state)



if __name__ == "__main__":
    unittest.main()
