#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import conf_parser
import json
import re

def parse(page, raw_page, url, parse_conf, page_encoding=None, source=None):
    tasks = []
    try:
        owner_id = int(re.findall("owner_id=(\d+)", url)[0])
        if owner_id < 499999999:
            for i in xrange(1, 4):
                n_owner_id = owner_id + i
                tasks.append(('article_detail_vk', re.sub('owner_id=\d+', 'owner_id=%s' % n_owner_id, url)))
    except Exception, e:
        print e
        pass
    items = []
    try:
        item = {}
        page_obj = json.loads(page)
        item['content'] = page
        items.append(item)
    except Exception, e:
       print e
       pass
    return tasks, items
