#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    try:
        page_obj = json.loads(page)
    except Exception, e:
        logging.error("Failed to load page, msg: %s" % e)
        return None, None
    tasks = []
    items = []
    image_path = page_obj.get('image_path', '')
    try:
        if image_path and type(image_path) is unicode:
            page_obj['image_path'] = 'http://fuss10.elemecdn.com' + image_path
        page_obj['title'] = page_obj['name']
        items.append(page_obj)
    except Exception, e:
        logging.error("Failed to get image path, msg: %s" % e)
    return tasks, items
