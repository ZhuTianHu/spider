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
    for data in page_obj:
        for food in data.get('foods', []):
            try:
                image_path = food.get('image_path', '')
                if image_path and type(image_path) is unicode:
                    food['image_path'] = 'http://fuss10.elemecdn.com' + image_path
                food['title'] = food['name']
                items.append(food)
            except Exception, e:
                logging.error("Failed to parse page, msg: %s" % e)
                continue
    return tasks, items
