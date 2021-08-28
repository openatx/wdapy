# coding: utf-8
#

import enum
import typing
import abc


def smart_value_of(obj, data: dict):
    for key, val in data.items():
        setattr(obj, key, val)


class Recover(abc.ABC):
    @abc.abstractmethod
    def recover(self) -> bool:
        pass


class DeviceInfo:
    pass


class StatusInfo:
    ip: str
    session_id: str

    @staticmethod
    def value_of(data: dict) -> "StatusInfo":
        info = StatusInfo()
        value = data['value']
        info.session_id = data['sessionId']
        info.ip = value['ios']['ip']
        return info
