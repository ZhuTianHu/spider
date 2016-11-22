#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import conf_parser
import re




def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    new_tasks = []
    for task_type, task_url in tasks:
        if task_type != '58_type1_detail':
            new_tasks.append((task_type, task_url))
            continue
        if task_url.find('entinfo') <= 0:
            new_tasks.append((task_type, task_url))
            continue
        task_url_list = task_url.split('?')
        if len(task_url_list) < 2:
            new_tasks.append((task_type, task_url))
            continue
        entinfo = ''
        target = ''
        for v in task_url_list[1].split('&'):
            if 'entinfo' in v:
                entinfo = v
                continue
            if 'target' in v:
                target = v
        new_url = task_url_list[0] + '?' + v
        if target:
            new_url += '&' + target
        new_tasks.append((task_type, new_url))
    return new_tasks, items
