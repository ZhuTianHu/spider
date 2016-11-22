#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import conf_parser


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    new_tasks = []
    for task_type, task_url in tasks:
        if task_type == 'icbc_office_detail':
            new_url = ("http://116.213.115.38/thememap/icbc_bank/json/"
                       "getResultByKeywordJson.jsp?Province=%s&City=&"
                       "Keyword=&pageno=1&pagesize=10&Type=0" % task_url)
            new_tasks.append((task_type, new_url))
        else:
            new_tasks.append((task_type, task_url))
    return new_tasks, items
