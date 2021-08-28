# coding: utf-8
#

import enum


class RequestMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"


GET = RequestMethod.GET
POST = RequestMethod.POST
