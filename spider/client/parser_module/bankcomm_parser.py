#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import urllib


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks = []
    items = []
    try:
        page_obj = json.loads(page)
    except Exception, e:
        print e
        return None, None
    for _, data in page_obj.get('data',{}).iteritems():
        try:
            phone = []
            if data.get('o', ''):
                phone.append(eval(repr(urllib.unquote(data['o'])).lstrip('u')).decode(page_encoding))
            if data.get('p', ''):
                phone.append(eval(repr(urllib.unquote(data['p'])).lstrip('u')).decode(page_encoding))
            items.append({
                'title': urllib.unquote(data.get('n', '')),
                'address': eval(repr(urllib.unquote(data['a'])).lstrip('u')).decode(page_encoding),
                'phone': phone
            })
        except Exception, e:
            print e
            continue
    return tasks, items
