#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging

from tornado.log import LogFormatter as _LogFormatter


class LogFormatter(_LogFormatter, object):
    """Init tornado.log.LogFormatter from logging.config.fileConfig"""
    def __init__(self, fmt=None, datefmt=None, color=True, *args, **kwargs):
        if fmt is None:
            fmt = _LogFormatter.DEFAULT_FORMAT
        super(LogFormatter, self).__init__(color=color, fmt=fmt, *args, **kwargs)

