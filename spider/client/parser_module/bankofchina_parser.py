#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import conf_parser

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, 
                                     parse_conf, page_encoding) 
    new_tasks = []
    for task_type, url in tasks:
        if task_type == 'bankofchina':
            try:
                new_url = ("http://srh.bankofchina.com/search/operation"
                           "/search.jsp?page=%s" % int(url))
                new_tasks.append((task_type, new_url))
            except Exception, e:
                print url, e
                continue
        else:
            new_tasks.append((task_type, url))
    return new_tasks, items
