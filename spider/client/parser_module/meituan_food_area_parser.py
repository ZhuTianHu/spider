#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import conf_parser

def get_next_page_url(url):
    """get next page url of restaurant list"""
    try:
        start_pos = url.find('page_index=')
        if start_pos < 0: return ''
        end_pos = url.find('&', start_pos)
        page_index = int(url[start_pos + len('page_index='): end_pos])
        page_index += 1
        new_url = (url[:start_pos + len('page_index=')] + str(page_index) +
                   url[end_pos:])
    except Exception, e:
        logging.error("Failed to get next page url, msg: %s" % e)
        return ''
    return new_url


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    if not tasks:
        return tasks, items
    next_page_url = get_next_page_url(url)
    if next_page_url: 
        tasks.append(('meituan_food_area', next_page_url))

    return tasks, items
