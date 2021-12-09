#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Created on Thu Dec 09 2021 10:30:41 by codeskyblue
"""

import logging
from ._proto import NAME
from logzero import setup_logger

logger = setup_logger(NAME, level=logging.INFO)
