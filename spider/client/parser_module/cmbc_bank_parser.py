#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks = []
    items = []
    try:
        page = page[page.find('{'): page.find(')')]
        page_obj = json.loads(page)
    except Exception, e:
        print e
        return None, None
    try:
        if page_obj['page'] < page_obj['pageCount']:
            tasks.append(('cmbc_bank', 
                          url.replace("page=%s" % page_obj['page'],
                                      "page=%s" % (page_obj['page'] + 1))))
    except Exception, e:
        print e
        pass

    for data in page_obj.get('list', []):
        try:
            data['title'] = data['bankname']
            data['phone'] = data['banktel']
            items.append(data)
        except Exception, e:
            print e
            continue
    return tasks, items
