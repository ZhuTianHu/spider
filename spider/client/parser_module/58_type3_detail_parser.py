#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import conf_parser
import re
import requests
import json




def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    if len(items) > 0:
        if 'comment_num' in items[0]:
            headers = headers = {'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'}
            comment_num = re.findall('(\d+)', items[0]['comment_num'])[0]
            items[0]['comment_num'] = comment_num
            if int(comment_num) > 0:
                cateid = re.findall('var _cateid\s*=\s*(\d+)\s*;', page)[0]
                #objectid = re.findall('zuche/(\d+)x\.shtml', url)[0]
                objectid = re.findall('entinfo=(\d+)', url)[0]
                items[0]['objectid'] = objectid
                userid = re.findall('var\s*_userid\s*=\s*(\d+)\s*;', page)[0]
                comment_url = "http://comment.58.com/comment/pc/listByCateid/1/?callback=getInfoJson1464073500495&userid=%s&cateid=%s&objectid=%s&objecttype=1&star=0" % (userid, cateid, objectid)
                comments = {}
                for i in xrange(3):
                    try:
                        comment_page = requests.get(comment_url, headers=headers, timeout=30).text
                        comment_page = comment_page.strip()
                        if len(comment_page) <= 0:
                            continue
                        comment_page = comment_page[comment_page.find('(') + 1: comment_page.rfind(')')]
                        comments = json.loads(comment_page)
                        break
                    except Exception, e:
                        continue
                items[0]['comment'] = comments
                items[0]['comment_url'] = comment_url
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
