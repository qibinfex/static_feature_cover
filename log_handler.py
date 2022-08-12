#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import logging
from settings import LOG_LOCATION
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(LOG_LOCATION, maxBytes=1000000, backupCount=300)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
