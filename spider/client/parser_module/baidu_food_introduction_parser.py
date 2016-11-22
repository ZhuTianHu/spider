import conf_parser
import re

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    if items:
        try:
            delivery_min_price = re.findall('(?:"takeout_price":")\s*(\d+)',
                                            page)[0]
            items[0]['delivery_min_price'] = delivery_min_price
        except:
            pass
        try:
            delivery_price = re.findall('(?:"takeout_cost":")\s*(\d+)', page)[0]
            items[0]['delivery_price'] = delivery_price
        except: 
            pass
        try:
            delivery_time = re.findall('(?:"delivery_time":")\s*(\d+)', page)[0]
            items[0]['delivery_time'] = delivery_time
        except:
            pass
    return (tasks, items)

