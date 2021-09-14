# coding: utf-8
#

import logging
import enum

logger = logging.getLogger("wdapy")

DEFAULT_WDA_URL = "http://localhost:8100"

class RequestMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"


GET = RequestMethod.GET
POST = RequestMethod.POST


class AppState(enum.IntEnum):
    STOPPED = 1
    BACKGROUND = 2
    RUNNING = 4


class Orientation(str, enum.Enum):
    LANDSCAPE = 'LANDSCAPE'
    PORTRAIT = 'PORTRAIT'
    LANDSCAPE_RIGHT = 'UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT'
    PORTRAIT_UPSIDEDOWN = 'UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN'
