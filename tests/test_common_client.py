# coding: utf-8
#

import unittest
from unittest.mock import MagicMock
from wdapy import AppiumClient


class SimpleTest(unittest.TestCase):
    def setUp(self):
        print("setup")
        self._client = AppiumClient(None)

    def test_status(self):
        self._client.request = MagicMock(return_value={
            "sessionId": "yyds",
            "value": {
                "ios": {
                    "ip": "1.2.3.4",
                }
            }
        })
        st = self._client.status()
        self.assertEqual("1.2.3.4", st.ip)
        self.assertEqual("yyds", st.session_id)


if __name__ == "__main__":
    unittest.main()
