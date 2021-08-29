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


if __name__ == "__main__":
    unittest.main()
