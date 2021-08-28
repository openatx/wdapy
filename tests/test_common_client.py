# coding: utf-8
#

import unittest
from unittest.mock import MagicMock
from wdapy import AppiumClient


class SimpleTest(unittest.TestCase):
    def setUp(self):
        print("setup")
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


if __name__ == "__main__":
    unittest.main()
