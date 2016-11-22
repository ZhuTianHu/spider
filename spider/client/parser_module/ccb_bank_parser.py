#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import conf_parser


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    new_tasks = []
    for task_type, task_url in tasks:
        if task_type == 'ccb_bank':
            try:
                page_num = int(task_url)
            except:
                continue
            new_url = url[:url.find('&pageNo=')] + '&pageNo=' + str(page_num)
            new_tasks.append(('ccb_bank', new_url))
    return new_tasks, items
