#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Tue Sep 14 2021 15:24:46 by codeskyblue
"""

import typing
from wdapy.exceptions import RequestError
from ._proto import *
from ._base import BaseClient
from ._logger import logger


class Alert:
    def __init__(self, client: BaseClient):
        self._client = client
    
    @property
    def exists(self) -> bool:
        try:
            self.get_text()
            return True
        except RequestError:
            return False

    def buttons(self) -> typing.List[str]:
        return self._client.session_request(GET, "/wda/alert/buttons")["value"]
    
    def get_text(self) -> str:
        return self._client.session_request(GET, "/alert/text")["value"]
    
    def accept(self):
        return self._client.session_request(POST, "/alert/accept")
    
    def dismiss(self):
        return self._client.session_request(POST, "/alert/dismiss")

    def click(self, button_name: typing.Union[str, list]):
        if isinstance(button_name, str):
            self._client.session_request(POST, "/alert/accept", {"name": button_name})
            return
        elif isinstance(button_name, list):
            expect_buttons = button_name
            buttons = self.buttons()
            for name in expect_buttons:
                if name in buttons:
                    return self.click(name)
            logger.debug("alert not clicked, buttons: %s, expect buttons: %s", buttons, expect_buttons)