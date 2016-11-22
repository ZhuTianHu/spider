#coding: utf-8
import conf_parser
import json
import requests
import urlparse

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    try:
        city = urlparse.urlparse(url).path.strip('/')
        req_url = "http://www.justdial.com/autosuggest.php?cases=popular&city=%s&scity=autosuggest.php?cases=popular&city=%s" % (city, city)
        page = requests.get(req_url, timeout=30, \
                headers={'User-Agent': '5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'})
        page_obj = json.loads(page.text)
        print page_obj.get('results', []) 
        tasks = []
        items = []
        for each in page_obj.get('results', []):
            for res in each:
                tasks.append(('justdial_category', res.get('href', '')))
    except:
        return [], []
    return tasks, items
