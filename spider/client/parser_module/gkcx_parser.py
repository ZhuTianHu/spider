#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import re

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks = []
    items = []
    try:
        page = page[page.find('{'): page.rfind(')')].strip()
        page = re.sub('(\s)', '', page)
        page_obj = json.loads(page)
    except Exception, e:
        print e
        return None, None
    try:
        url_obj = url.split('&')
        cur_page = 1
        page_size = 10
        index = 0
        for param in url_obj:
            if param.startswith('page'):
                cur_page = int(param[param.find('=') + 1:])
                url_obj[index] = 'page=' + str(cur_page + 1)
            if param.startswith('size'):
                page_size = int(param[param.find('=') + 1:])
            index += 1
        if cur_page * page_size < int(page_obj['totalRecord']['num']):
            new_url = '&'.join(url_obj)
            tasks.append(('gkcx', new_url))

        for data in page_obj['school']:
            school_id = data.get('schoolid', '')
            if not school_id:
                continue
            tasks.append(('gkcx_detail',
                          'http://gkcx.eol.cn/schoolhtm/schoolTemple/school%s.htm' 
                          % school_id))
    except Exception, e:
        print e
    return tasks, items
