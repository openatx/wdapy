"""
See
- https://www.w3.org/TR/webdriver/#actions
- https://appium.github.io/appium.io/docs/en/commands/interactions/actions/#http-api-specifications

Usage example:
    # 起点142, 240 画一个长度为100的正方形
    finger1 = TouchActions.pointer("finger1", actions=[
        PointerAction.move(142, 240, origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.pause(1000),
        PointerAction.move(0, 100, origin=Origin.POINTER),
        PointerAction.pause(1000),
        PointerAction.move(100, 0, origin=Origin.POINTER),
        PointerAction.pause(1000),
        PointerAction.move(0, -100, origin=Origin.POINTER),
        PointerAction.pause(1000),
        PointerAction.move(-100, 0, origin=Origin.POINTER),
        PointerAction.up(),
    ])
    client.perform_actions([finger1])
"""
__all__ = [
    "TouchActionType",
    "PointerActionType",
    "KeyActionType",
    "PointerType",
    "Origin",
    "PointerAction",
    "KeyAction",
    "Parameters",
    "TouchActions",
]

from enum import Enum

from typing import List, Optional, Union
from pydantic import BaseModel

from ._proto import POST
from ._base import BaseClient

class TouchActionType(str, Enum):
    POINTER = "pointer"
    KEY = "key"
    NULL = "null"


class PointerActionType(str, Enum):
    POINTER_MOVE = "pointerMove"
    POINTER_DOWN = "pointerDown"
    POINTER_UP = "pointerUp"
    PAUSE = "pause"

class KeyActionType(str, Enum):
    KEY_DOWN = "keyDown"
    KEY_UP = "keyUp"

class PointerType(str, Enum):
    TOUCH = "touch"
    MOUSE = "mouse"
    PEN = "pen"

class Origin(str, Enum):
    VIEWPORT = "viewport"
    POINTER = "pointer"
    # or: {'element-6066-11e4-a52e-4f735466cecf': ''} # not tested


class PointerAction(BaseModel):
    type: PointerActionType
    duration: Optional[int] = None
    x: Optional[int] = None
    y: Optional[int] = None
    origin: Optional[Origin] = None
    button: Optional[int] = None

    @staticmethod
    def move(x: int, y: int, *, duration: int=100, origin: Origin = Origin.VIEWPORT) -> "PointerAction":
        """
        Move pointer to (x, y) with duration(ms)
        
        Args:
            x: x coordinate
            y: y coordinate
            duration: duration(ms) default 100
            origin: pointer(relative to last position) or viewport(relative to (0, 0))
        """
        # pointerMove $x, $y, $duration
        # same as
        # pause $duration
        # pointerMove $x, $y, duration=0
        return PointerAction(type=PointerActionType.POINTER_MOVE, x=x, y=y, duration=duration, origin=origin)

    @staticmethod
    def down() -> "PointerAction":
        # button=0 # left
        return PointerAction(type=PointerActionType.POINTER_DOWN, button=0)

    @staticmethod
    def up() -> "PointerAction":
        return PointerAction(type=PointerActionType.POINTER_UP, button=0)

    @staticmethod
    def pause(duration: int) -> "PointerAction":
        return PointerAction(type=PointerActionType.PAUSE, duration=duration)


class KeyAction(BaseModel):
    type: KeyActionType
    value: str

    @staticmethod
    def down(value: str) -> "KeyAction":
        return KeyAction(type=KeyActionType.KEY_DOWN, value=value)

    @staticmethod
    def up(value: str) -> "KeyAction":
        return KeyAction(type=KeyActionType.KEY_UP, value=value)


class Parameters(BaseModel):
    pointerType: PointerType


class TouchActions(BaseModel):
    type: TouchActionType
    id: str
    parameters: Optional[Parameters] = None
    actions: Union[List[PointerAction], List[KeyAction]]

    @staticmethod
    def pointer(id: str, actions: List[PointerAction], pointer_type: PointerType = PointerType.TOUCH) -> "TouchActions":
        return TouchActions(
            type=TouchActionType.POINTER,
            id=id,
            parameters=Parameters(pointerType=pointer_type),
            actions=actions
        )

    @staticmethod
    def key(id: str, actions: List[KeyAction]) -> "TouchActions":
        return TouchActions(type=TouchActionType.KEY, id=id, actions=actions)

    @staticmethod
    def null(id: str) -> "TouchActions":
        return TouchActions(type=TouchActionType.NULL, id=id, actions=[])


class TouchActionsClient(BaseClient):
    def perform_actions(self, actions: List[TouchActions]):
        self.session_request(POST, "/actions", {"actions": [a.model_dump(exclude_none=True) for a in actions]})