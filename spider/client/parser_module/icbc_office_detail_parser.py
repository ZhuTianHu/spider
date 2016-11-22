#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import re


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    page1 = re.sub('([a-zA-Z_]+)(?=:)', r"'\1'", page.strip().strip("var APRSA ="))
    page2 = re.sub("'", '"', page1)
    page3 = re.sub('(\s+)', ' ', page2)
    page_obj = json.loads(page3)
    tasks = []
    items = []
    try:
        total_page = page_obj['totalpage']
        cur_page = page_obj['pn']
        if cur_page < total_page:
            start_pos = url.find('pageno=')
            end_pos = url.find('&pagesize')
            task_url = (url[:start_pos] + 'pageno=' + str(cur_page + 1) +
                        url[end_pos:])
            tasks.append(('icbc_office_detail', task_url))

    except Exception, e:
        print e
        pass
    try:
        for data in page_obj['result']:
            data['title'] = data['cname']
            data['address'] = data['caddress']
            data['phone'] = []
            data['phone'].append(data['pphone'])
            data['phone'].append(data['sphone'])
            items.append(data)
    except Exception, e:
        pass
    return tasks, items
