#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks = []
    items = []
    try:
        page_obj = json.loads(page)
    except: 
        return None, None
    for data in page_obj.get('data', []):
        try:
            tasks.append(('meituan_food_area', "http://i.waimai.meituan.com/home/%s?page_index=0&apage=1"
                             % data['geo_id']))
        except:
            continue
    return tasks, items


