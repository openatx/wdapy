# coding: utf-8
#

import enum

NAME = "wdapy"
DEFAULT_WDA_URL = "http://localhost:8100"
DEFAULT_HTTP_TIMEOUT = 90


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


class Keycode(str, enum.Enum):
    HOME = "home"
    VOLUME_UP = "volumeUp"
    VOLUME_DOWN = "volumeDown"

    # allow only for press_duration
    POWER = "power"
    SNAPSHOT = "snapshot"
    POWER_PLUS_HOME = "power_plus_home"


class GestureAction(str, enum.Enum):
    TAP = "tap"
    PRESS = "press"
    MOVE_TO = "moveTo"
    WAIT = "wait"
    RELEASE = "release"


class BatteryState(enum.IntEnum):
    Unknown = 0
    Unplugged = 1
    Charging = 2
    Full = 3
