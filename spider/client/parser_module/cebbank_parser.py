#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks = []
    items = []
    try:
        page_obj = json.loads(page)
    except Exception, e:
        print e
        return None, None
    for data in page_obj.get('dotList', []):
        try:
            del data['id']
            items.append(data)
        except Exception, e:
            print e
            continue
    return tasks, items
