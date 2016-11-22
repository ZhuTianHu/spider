#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urlparse
import logging

def get_next_area_url(url):
    """get next page url of restaurant list"""
    try:
        start_pos = url.find('offset=')
        if start_pos < 0: return ''
        end_pos = url.find('&', start_pos)
        offset_value = int(url[start_pos + len('offset='): end_pos])
        offset_value += 30
        new_url = (url[:start_pos + len('offset=')] + str(offset_value) +
                   url[endpos:])
    except Exception, e:
        logging.error("Failed to get next area url, msg: %s" % e)
        return ''
    return new_url


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks = []
    items = []
    try:
        page_obj = json.loads(page)
    except Exception, e:
        logging.error("Failed to load page, msg: %s" % e)
        return None, None
    if type(page_obj) is not list:
        return None, None
    for data in page_obj:
        name_for_url = data.get('name_for_url', '')
        if not name_for_url: continue
        try:
            geohash = urlparse.parse_qs(
                urlparse.urlparse(url).query)['geohash'][0]
            if not geohash: continue
        except Exception, e:
            logging.error("Failed to get geohash, msg: %s" % e)
            continue
        tasks.append(('ele_me_food_detail',
                      'http://m.ele.me/restapi/v1/restaurants/%s/menu?'
                      'geohash=%s'
                      % (name_for_url, geohash)))
        tasks.append(('ele_me_food_restaurant',
                      'http://m.ele.me/restapi/v1/restaurants/%s?'
                      'extras[]=restaurant_activity&extras[]=license&geohash=%s'
                      % (name_for_url, geohash)))
    if not tasks:
        return tasks, items
    next_area_url = get_next_area_url(url)
    if next_area_url: 
        tasks.append(('ele_me_food_area', next_area_url))

    return tasks, items
