#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import urllib

sys.path.append("../../")
import getpage


def parse_query_file():
    for line in open("/search/sliu/ypdata/addr/dianping"):
        line = line.strip()
        line_obj = line.split('\t')
        city = line_obj[0].strip().decode('utf-8')
        query_word = urllib.quote(line_obj[1].strip())
        yield city, query_word

def init_site(site_info):
    city_code = json.loads(open('init_module/baidu_city_code.txt').read())
    init_urls = []
    for city, query_word in parse_query_file():
        req_url = ("http://waimai.baidu.com/waimai?qt=poisug&wd=%s&"
                   "cb=suggestion_1442286608299&cid=%s&b=&type=0&"
                   "newmap=1&ie=utf-8&callback=jsonp11"
                   % (query_word, city_code[city]))
        resp = getpage.get(req_url, use_proxy=0)
        if not resp or not resp.text:
            continue
        start_pos = resp.text.find('{')
        end_pos = resp.text.rfind('}') + 1
        if end_pos < 0:
            return init_urls
        text = resp.text[start_pos: end_pos]
        resp_obj = json.loads(text)
        for data in resp_obj.get('s', []):
            data_obj = data.split('$')
            if not data_obj: continue
            try:
                address = urllib.quote(data_obj[3].encode('utf-8'))
                lat = data_obj[5].split(',')[0]
                lng = data_obj[5].split(',')[1]
                init_urls.append("http://waimai.baidu.com/mobile/waimai?qt=shoplist&address=%s&"
                                 "lat=%s&lng=%s&page=1&count=20&display=json"
                                 % (address, lat, lng))
            except Exception, e:
                print e
                continue
    return init_urls
        


