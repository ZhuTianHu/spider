#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    page_obj = json.loads(page)
    tasks = []
    items = []
    try:
        if page_obj['BranchSearchRests']:
            url = url.strip()
            start_pos = url.find('&i=')
            cur_page = int(url[start_pos + len('&i='):])
            next_page_url = ("http://app.abchina.com/branch/common/"
                             "BranchService.svc/Branch?p=-1&c=-1&b=-1&q=&t=0&i=%s"
                             % (cur_page + 1))
            tasks.append(('abchina', next_page_url))
    except Exception, e:
        print e
        pass
    for data in page_obj.get('BranchSearchRests', []):
        item = {}
        for k, v in data.get('BranchBank', {}).iteritems():
            if k != 'PhoneNumber':
                item[k.lower()] = v
            else:
                item['phone'] = v
        items.append(item)
    return tasks, items
