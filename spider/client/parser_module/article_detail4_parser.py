#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging

import lxml.html
import lxml.etree
import tldextract

from parser_module.content_extract import content_extract


def parse(page, raw_page, url, parse_conf, page_encoding=None, source=None):
    """Extract list url of page"""
    ret_tasks = []
    ret_items = []

    if not page or not parse_conf:
        return (ret_tasks, ret_items)

    # extract content 
    try:
        time, title, content = content_extract.parse(url, page)
    except Exception, e:
        logging.error("Failed to parse page %s, msg: %s" % (url, e))
        return (ret_tasks, ret_items)
    if title or content:
        ret_items.append({
            'title': title, 
            'content': content
        })
    return (ret_tasks, ret_items)

