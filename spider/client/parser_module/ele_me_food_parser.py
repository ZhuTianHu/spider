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
            tasks.append(('ele_me_food_area', "http://m.ele.me/restapi/v1/restaurants?"
                          "extras[]=restaurant_activity&extras[]=food_activity"
                          "&geohash=%s&is_premium=0&limit=30"
                          "&offset=0&type=geohash" % data['geohash']))
        except:
            continue

    return tasks, items

