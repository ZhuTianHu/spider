#coding: utf-8
import conf_parser
import requests

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    try:
        prospect_id = url.split('.')[-2].split('_')[-1]
        city = url.split('.')[-2].split('_')[-2]
        phone_url = ("http://www.indiacom.com/rwd/asp/getphone.asp"
                     "?districtcd=%s&Prospectid=%s" % (city, prospect_id))
        resp = requests.get(phone_url, headers={'Referer': url})
        phone = resp.text
        if phone:
            items[0]['phone'] = phone
    except:
        pass
    return tasks, items
