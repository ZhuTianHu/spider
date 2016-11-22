#coding: utf-8

import json
def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    try:
        page = page[page.find('(')+1:-1]
        page = json.loads(page)
    except Exception,e:
        return (None, None)
    data = page['Data']
    if not data:
        return (None, None)
    ret_urls = [] 
    ret_items = []
    city_url = "http://116.228.70.245:8088/BDM/OutWebService/StationPlace/FindStatonPage?StationCode=%s&callback=jsonp1426584123768"
    for d in data:
        url = city_url %d['StationCode']
        ret_urls.append((parse_conf['root'][0]['name'], url))
    return (ret_urls, ret_items)


