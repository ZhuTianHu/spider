#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import conf_parser
import re
import requests
import json


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    if len(items) > 0:
        try:
            contacts = re.findall("linkman:'(.*?)'", page)[0]
            items[0]['contacts'] = contacts
        except Exception, e:
            print e
            pass
        try:
            headers = headers = {'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'}
            uid = re.findall("uid\s*:\s*'(\d+)", page)[0]
            userdata_url = "http://user.58.com/userdata/?callback=jsonp567&userid=%s&type=26" % uid
            for i in xrange(3):
                try:
                    userdata_page = requests.get(userdata_url, headers=headers, timeout=30).text
                    company_title = re.findall("corpname\s*:\s*'\s*(.*?)'", userdata_page)[0]
                    if len(company_title) > 0:
                        items[0]['company_title'] = company_title
                        break
                except Exception, e:
                    print e
                    continue
        except Exception, e:
            print e
            pass

        if 'description_address' in items[0] and type(items[0]['description_address']) is list:
            items[0]['description_address'] = ''.join(items[0]['description_address'])
        if 'description_content' in items[0] and type(items[0]['description_content']) is list:
            items[0]['description_content'] = '\n'.join(items[0]['description_content'])
        if 'ext_info' in items[0]:
            new_ext_info = []
            ext_info = items[0]['ext_info']
            if type(ext_info) is not list:
                ext_info = [ext_info]
            for v in ext_info:
                value = v.get('value', [])
                if type(value) is list:
                    if len(value) > 1:
                        new_ext_info.append({'key': value[0], 'value': ''.join(value[1:])})
                    if len(value) == 1:
                        new_ext_info.append({'value': value[0]})
                else:
                    new_ext_info.append({'value': value})
            if new_ext_info:
                items[0]['ext_info'] = new_ext_info
    return tasks, items
