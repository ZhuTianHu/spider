#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import urllib

from traceback import format_exc 


def get_next_page_url(url):
    """get next page url of restaurant list"""
    try:
        start_pos = url.find('page=')
        if start_pos < 0: return ''
        end_pos = url.find('&', start_pos)
        page_index = int(url[start_pos + len('page='): end_pos])
        page_index += 1
        new_url = (url[:start_pos + len('page=')] + str(page_index) +
                   url[end_pos:])
    except Exception, e:
        logging.error("Failed to get next page url, msg: %s" % e)
        return ''
    return new_url


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks = []
    items = []
    try:
        page_obj = json.loads(page)
        shop_info_list = page_obj['result']['shop_info']
        address = urllib.quote(page_obj['params']['address'].encode('utf-8'))
        if not shop_info_list: 
            return tasks, items
    except Exception, e:
        logging.error("Failed to get shop info list, msg: %s" % e)
        return tasks, items
    for shop_info in shop_info_list:
        if not shop_info:
            continue
        try:
            shop_info['title'] = shop_info['shop_name']
            items.append(shop_info)
            shop_id = shop_info['shop_id']
            shop_lng = shop_info['shop_lng']
            shop_lat = shop_info['shop_lat']

            tasks.append(('baidu_food_detail',
                          "http://waimai.baidu.com/mobile/waimai?qt=shopmenu&"
                          "is_attr=1&shop_id=%s&address=%s&lat=%s&lng=%s"
                          % (shop_id, address, shop_lat, shop_lng)))
        except Exception, e:
            logging.info(format_exc())
            logging.error("Failed to parse %s by parser, msg: %s" % (url, e))
            continue
    if not tasks:
        return tasks, items
    next_page_url = get_next_page_url(url)
    if next_page_url: 
        tasks.append(('baidu_food', next_page_url))

    return tasks, items
