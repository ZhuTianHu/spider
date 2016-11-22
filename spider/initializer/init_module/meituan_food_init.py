#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import urllib


def parse_query_file():
    for line in open("/search/sliu/ypdata/addr/dianping"):
        line = line.strip()
        line_obj = line.split('\t')
        city = urllib.quote(line_obj[0].strip())
        query_word = urllib.quote(line_obj[1].strip())
        yield city, query_word

def init_site(site_info):
    city_code = json.loads(open('init_module/meituan_city_code.txt').read())
    init_urls = []
    for city, query_word in parse_query_file():
        req_url = ("http://i.waimai.meituan.com/%s/search?address=%s"
                   % (city, query_word))
        init_urls.append(req_url)
    return init_urls
        


