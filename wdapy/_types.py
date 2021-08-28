# coding: utf-8
#

import enum
import typing
import abc


class WindowSize(typing.NamedTuple):
    width: int
    height: int


def smart_value_of(obj, data: dict):
    for key, val in data.items():
        setattr(obj, key, val)


class Recover(abc.ABC):
    @abc.abstractmethod
    def recover(self) -> bool:
        pass


class _Base:
    def __repr__(self):
        attrs = []
        for k, v in self.__dict__.items():
            attrs.append(f"{k}={v!r}")
        return f"<{self.__class__.__name__} " + ",".join(attrs) + ">"


class StatusInfo(_Base):
    ip: str
    session_id: str
    message: str

    @staticmethod
    def value_of(data: dict) -> "StatusInfo":
        info = StatusInfo()
        value = data['value']
        info.session_id = data['sessionId']
        info.ip = value['ios']['ip']
        info.message = value['message']
        return info


class DeviceInfo:
    pass
